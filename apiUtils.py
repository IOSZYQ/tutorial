__author__ = 'swolfod'

from utilities import utils
import collections
import re
import json
from django.core import cache
from django.core.serializers.json import DjangoJSONEncoder
from django_redis import get_redis_connection
import html
from datetime import datetime
import random

paragraphTags = ["p", "h3", "h4", "blockquote", "img", "hr"]
contentPartTags = ["b", "strong", "i", "em", "u", "a", "br", "span"]
clearTags = ["span", "font"]
MAX_FETCH_COUNT = 12000


def getValueByPath(data, path):
    path = path.split(".")
    for segment in path:
        if segment.endswith("[]"):
            segment = segment[:len(segment) - 2]

        if isinstance(data, list):
            data = [ele.get(segment) if ele else None for ele in data]
        else:
            data = data.get(segment)

        if not data:
            break

    return data


def setValueByPath(data, path, value, strict=False):
    if data is None:
        return

    if isinstance(data, list):
        if not isinstance(value, list) or (strict and len(value) != len(data)):
            raise Exception()

        i = 0
        while i < len(data) and i < len(value):
            setValueByPath(data[i], path, value[i], strict)
            i += 1
    else:
        if "." not in path:
            data[path] = value
            return

        splitterIndex = path.index(".")
        currentSeg = path[:splitterIndex]
        remainingPath = path[splitterIndex + 1:]
        setValueByPath(data[currentSeg], remainingPath, value, strict)



def popValueByPath(data, path, default=None):
    path = path if isinstance(path, list) else path.split(".")

    for i in range(len(path) - 1):
        if isinstance(data, list):
            return [popValueByPath(item, path[i+1:], default) for item in data]

        data = data.get(path[i])
        if not data:
            return

    if isinstance(data, list):
        return [item.pop(path[-1], default) for item in data]
    else:
        return data.pop(path[-1], default)


def popFields(rootFields, fieldsPathList, keepPath=True):
    result = {}

    if not isinstance(fieldsPathList, list):
        fieldsPathList = [fieldsPathList]

    for path in fieldsPathList:
        try:
            fields = getValueByPath(rootFields, path)
        except:
            continue

        if fields is not True and fields is not None:
            try:
                setValueByPath(rootFields, path, True if keepPath else False)
            except:
                pass

        result[path] = fields

    return result


def collectValues(objList, pathList):
    values = set()

    if not isinstance(pathList, list):
        pathList = [pathList]

    for obj in objList:
        for path in pathList:
            try:
                value = getValueByPath(obj, path)
            except:
                continue

            if isinstance(value, list):
                values = values.union(utils.deepFlatten(value))
            else:
                values.add(value)

    return values


def combinePathFields(fieldsDict, *paths):
    return combineFields(*[fieldsDict[path] for path in paths])


def combineFields(*fieldsList):
    result = {}

    for fields in fieldsList:
        emptyResult = result is True or not result
        if fields is True and emptyResult:
            result = True
        elif fields != None:
            if emptyResult:
                result = {}

            utils.deepUpdate(result, fields)

    return result


def deepUpdateFields(destFields, srcFields):
    for key, val in srcFields.items():
        if isinstance(val, collections.Mapping):
            deepUpdateFields(destFields.setdefault(key, {}), val)
        elif isinstance(val, list):
            destFields[key] = destFields.get(key, []) + val
        elif not isinstance(destFields.get(key), collections.Mapping):
            destFields[key] = srcFields[key]

    return destFields


def updateFieldValue(objList, pathList, fieldsDict, valueDict):
    if not isinstance(pathList, list):
        pathList = [pathList]

    def getFieldsValue(valueKey, fields):
        if not valueKey:
            return None

        if fields is True:
            return valueKey

        if isinstance(valueKey, list):
            return [getFieldsValue(key, fields) for key in valueKey]
        elif valueKey in valueDict:
            return utils.extractData(valueDict[valueKey], fields)

    for obj in objList:
        for path in pathList:
            fields = fieldsDict.get(path, None)
            if not fields:
                popValueByPath(obj, path)
                continue

            valueKey = getValueByPath(obj, path)
            if valueKey:
                value = getFieldsValue(valueKey, fields)
                setValueByPath(obj, path, value)


def clearContentJson(content):
    if content and type(content) is str:
        content = json.loads(content)
    pictures = []

    rawText = ""
    if content:
        for paragraph in content:
            if paragraph["tag"].lower() not in paragraphTags:
                paragraph["tag"] = "P"

            if paragraph["tag"].lower() == "img":
                imgSrc = clearParagraph(paragraph)
                pictures.append(imgSrc)
            else:
                rawText += clearParagraph(paragraph) + "\n"

        rawText = html.unescape(rawText).strip()

    return pictures, rawText, json.dumps(content, cls=DjangoJSONEncoder)


def clearParagraph(paragraph):
    if paragraph["tag"].lower() == "img":
        if paragraph["attributes"]:
            attributes = {}

            for attribute in paragraph["attributes"]:
                if isinstance(attribute, str):
                    if attribute == "src":
                        imgSrc = paragraph["attributes"][attribute]
                elif attribute["name"] == "src":
                    imgSrc = attribute["value"]

            try:
                if "data:" in imgSrc and "base64," in imgSrc:
                    startIdx = imgSrc.index("data:")
                    try:
                        endIdx = imgSrc.index("?")
                    except:
                        endIdx = len(imgSrc)

                    imgSrc = imgSrc[startIdx:endIdx]
                    imgSrc = images.utils.saveImageData(imgSrc)

                imgSrc = re.search(r'([a-zA-Z0-9]{32}_[0-9]+x[0-9]+)', imgSrc, re.IGNORECASE)
                attrValue = imgSrc.group(1)
                attributes["src"] = attrValue
            except:
                return ""

            paragraph["attributes"] = attributes
            return attributes.get("src", None)

        return None

    contentRawText = ""
    try:
        paragraph["contents"], contentRawText = clearContent(paragraph)
    except:
        paragraph["contents"] = [""]

    return contentRawText


def clearContent(element):
    cleanedContent = []
    rawText = ""
    for ele in element["contents"]:
        try:
            if isinstance(ele, str):
                if ele:
                    cleanedContent.append(ele)
                    rawText += ele
                continue

            eleTag = ele["tag"].lower()

            if eleTag not in contentPartTags or not ele["contents"]:
                continue

            eleContent, eleRawText = clearContent(ele)
            if eleTag in clearTags:
                cleanedContent += (eleContent)
            else:
                ele["contents"] = eleContent
                cleanedContent.append(ele)
            rawText += eleRawText
        except:
            continue

    return cleanedContent, rawText


def normalizeContent(content, fields=None):
    if content is None or content.strip() == "":
        return None

    if fields == "html":
        return contentJsonToHtml(content)

    content = json.loads(content)
    if content is None:
        return None

    for paragraph in content:
        if paragraph["tag"].lower() == "img":
            try:
                if "src" in paragraph:
                    imgSrc = imageUtils.patternImageUrl(paragraph["src"], 2)
                    paragraph["src"] = imgSrc
                    break

                if "attributes" in paragraph:
                    for attribute in paragraph["attributes"]:
                        if isinstance(attribute, str):
                            if attribute == "src":
                                imgSrc = imageUtils.patternImageUrl(paragraph["attributes"][attribute], 2)
                                paragraph["attributes"][attribute] = imgSrc
                        elif attribute["name"] == "src":
                                imgSrc = imageUtils.patternImageUrl(attribute["value"], 2)
                                attribute["value"] = imgSrc

            except:
                pass

    return json.dumps(content)



def extractDataFromDict(itemId, resultDict, srcDict, fields, missedIdSet=None):
    try:
        resultDict[itemId] = utils.extractData(srcDict[itemId], fields)
    except:
         if missedIdSet != None:
             missedIdSet.add(itemId)


def updateDataFromApi(idHash, srcApi, fields, dataDictList, branchKey=None, itemsKey=None):
    if not idHash:
        return

    if not isinstance(dataDictList, list):
        dataDictList = [dataDictList]

    items = srcApi.read(query={ "id": idHash, "branchKey": branchKey }, fields=fields)
    if isinstance(items, dict) and itemsKey:
        items = items[itemsKey]

    for item in items:
        for dataDict in dataDictList:
            dataDict[item["id"]] = item


def cleanListNullElement(data, path):
    if not data:
        return

    if not isinstance(data, list):
        data = [data]

    fields = path.split(".")
    for obj in data:
        if len(fields) == 1:
            if isinstance(obj.get(fields[0]), list):
                obj[fields[0]] = [item for item in obj[fields[0]] if item is not None]
            continue

        cleanListNullElement(obj.get(fields[0]), ".".join(fields[1:]))


def getCache():
    return cache.caches["redis"]


def sortedDataset(dataset, idList):
    dataList = list(dataset)
    idList = [int(id) for id in idList]
    dataList.sort(key=lambda obj:idList.index(obj.id))
    return dataList


def searchWithHighlights(last, start, count, searchFunc):
    if start:
        last = ""
    else:
        start = 0

    if not last:
        fetchedIds, totalCount, highlights = searchFunc(start, count)
        fetchedCnt = start + count
        return fetchedIds, totalCount > fetchedCnt and fetchedCnt < MAX_FETCH_COUNT, highlights, totalCount

    fetchCnt = 0
    canFetchMore = True

    while canFetchMore:
        fetchCnt = max(fetchCnt * 2, count, 1000)
        fetchCnt = min(fetchCnt, MAX_FETCH_COUNT)
        fetchedIds, totalCount, highlights = searchFunc(0, fetchCnt)
        canFetchMore = len(fetchedIds) < totalCount and fetchCnt < MAX_FETCH_COUNT

        if last in fetchedIds:
            lastIndex = fetchedIds.index(last)
            idList = fetchedIds[lastIndex + 1 : lastIndex + count + 1]
            if len(idList) < count and canFetchMore:
                idList, totalCount, highlights = searchFunc(lastIndex + 1, count)

            fetchedCnt = lastIndex + 1 + len(idList)

            return idList, totalCount > fetchedCnt and fetchedCnt < MAX_FETCH_COUNT, highlights, totalCount

    return [], False, {}, 0


def getCachedOrSearch(cacheKey, last, start, count, searchFunc, expiration=600):
    if start:
        last = ""
    else:
        start = 0


    redisClient = get_redis_connection("redis")
    totalCountKey = cacheKey + "-count"
    totalCount = redisClient.get(totalCountKey)
    idList = []
    hasMore = True
    cachedCnt = 0

    if totalCount != None:
        #redisClient.expire(totalCountKey, 600)
        totalCount = int(totalCount)
        if totalCount == 0:
            return [], False, totalCount

        idList = [int(id) for id in redisClient.lrange(cacheKey, start, -1 if last else start + count - 1) or []]
        cachedCnt = start + len(idList)
        hasMore = cachedCnt < totalCount
        #redisClient.expire(cacheKey, 600)

        if idList and last:
            try:
                lastIndex = idList.index(last)
                hasMore = hasMore or lastIndex + count + 1 < len(idList)
                idList = idList[lastIndex + 1 : lastIndex + count + 1]
            except:
                idList = []

    if len(idList) < count and hasMore:
        fetchCnt = 0
        canFetchMore = True

        while canFetchMore and len(idList) < count:
            fetchCnt = max(fetchCnt * 2, cachedCnt * 2, start + count * 20)

            if fetchCnt > MAX_FETCH_COUNT:
                fetchCnt = MAX_FETCH_COUNT

            fetchedIds, totalCount, highlights = searchFunc(0, fetchCnt)
            canFetchMore = len(fetchedIds) < totalCount and fetchCnt < MAX_FETCH_COUNT

            if last:
                if last in fetchedIds:
                    lastIndex = fetchedIds.index(last)
                    idList = fetchedIds[lastIndex + 1 : lastIndex + count + 1]
                else:
                    idList = []
            else:
                idList = fetchedIds[start : start + count]

        redisClient.set(totalCountKey, totalCount, ex=expiration)
        redisClient.delete(cacheKey)

        if totalCount > 0 and fetchedIds:
            redisClient.rpush(cacheKey, *fetchedIds)
            redisClient.expire(cacheKey, expiration)
            hasMore = (len(idList) > 0 and idList[-1] != fetchedIds[-1]) or canFetchMore
        else:
            hasMore = False

    return [int(id) for id in idList], hasMore, totalCount


def deleteCacheByPattern(patterns):
    if not isinstance(patterns, list):
        patterns = [patterns]

    cacheClient = get_redis_connection("redis")
    cache = getCache()

    for pattern in patterns:
        for key in cacheClient.scan_iter(pattern):
            cacheClient.delete(key)

        cache.delete_pattern(pattern)


def defaultSerial():
    epoch = datetime.utcfromtimestamp(0)
    ticks = int((datetime.utcnow() - epoch).total_seconds() * 100)
    return str(hex(ticks * 10000 + random.randint(0, 9999)))[2:]


def contentJsonToHtml(content):
    if content and type(content) is str:
        content = json.loads(content)

    html = ""
    for paragraph in content:
        if not paragraph:
            continue

        if isinstance(paragraph, str):
            html += paragraph
            continue

        tag = paragraph["tag"]
        children = paragraph.get("contents")
        buf = []

        def _buildAttr(attributes, buf):
            for attr in attributes:
                if isinstance(attr, str):
                    k = attr
                    v = attributes[attr]
                else:
                    k = attr["name"]
                    v = attr["value"]

                buf.append(' ' + k + '="')
                if (isinstance(v, list)):
                    buf.append(" ".join(v))
                elif k == "src":
                    imgW, imgH = utils.imageSize(v)
                    if not imgW or not imgH:
                        imgW = 2000
                        imgH = 2000
                    buf.append(imageUtils.patternImageUrl(v, 1, width=imgW, height=imgH))
                else:
                    buf.append(v)

                buf.append('"')

        buf.append('<')
        buf.append(tag)
        if paragraph.get("attributes"):
            _buildAttr(paragraph["attributes"], buf)

        buf.append('>')
        if children:
            buf.append(contentJsonToHtml(children))

        buf.append('</' + tag + '>')

        html += "".join(buf)

    return html
