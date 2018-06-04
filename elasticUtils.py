__author__ = 'swolfod'

import json
from django.core.serializers.json import DjangoJSONEncoder
from elasticsearch import Elasticsearch, helpers
from django.db.models import QuerySet


def getClient():
    return Elasticsearch(["http://127.0.0.1:9200/"])


def filteredQuery(query, filters):
    if not filters:
        return query

    if len(filters) > 1:
        filters = {
            "bool": {
                "must": filters
            }
        }
    else:
        filters = filters[0]

    return {
        "filtered": {
            "query": query,
            "filter": filters
        }
    }


def cleanElasticId(elasticId):
    if "_" in elasticId:
        elasticId = elasticId[:elasticId.index("_")]
    return int(elasticId)


def doSearch(query, start, count, order, index, docType, idOnly=True, highlight=None):
    searchBody = {
        "query": query,
        "fields": [],
        "from": start,
        "size": count
    }

    if highlight:
        searchBody["highlight"] = highlight

    if isinstance(order, str):
        fields = order.split(",")
        conditions = []

        for field in fields:
            field = field.strip()
            descendant = False
            if field[0] == "-":
                field = field[1:]
                descendant = True

            conditions.append({field: {"order": "desc" if descendant else "asc"}})

        if len(conditions) == 1:
            conditions = conditions[0]
        searchBody["sort"] = conditions
    elif order:
        searchBody["sort"] = order

    es = getClient()
    res = es.search(index=index, doc_type=docType, body=searchBody)

    result = res["hits"]
    total = result["total"]
    docs = []
    highlights = {}
    for meta in result["hits"]:
        docId = cleanElasticId(meta["_id"])

        docs.append(docId if idOnly else meta)

        if highlight:
            docHighlight = meta.get("highlight")
            if docHighlight:
                highlightFields = list(docHighlight.keys())
                for field in highlightFields:
                    fragments = docHighlight[field]
                    cleanedFragments = []

                    for fragment in fragments:
                        fragmentParts = fragment.split("<em>")
                        fragmentContent = [fragmentParts[0]]

                        for i in range(1, len(fragmentParts)):
                            subParts = fragmentParts[i].split("</em>")
                            fragmentContent.append({
                                "tag": "em",
                                "contents": [subParts[0]]
                            })

                            fragmentContent.append(subParts[1])

                        jsonDict = {
                            "tag": "span",
                            "contents": fragmentContent
                        }
                        cleanedFragments.append(json.dumps(jsonDict, cls=DjangoJSONEncoder))

                    docHighlight[field] = cleanedFragments

            highlights[docId] = docHighlight

    return docs, total, highlights


def resetIndex(indexName, config):
    indexConfig = config.Indices[indexName]
    indexBody = {
        "settings": indexConfig["settings"] if indexConfig.get("settings") else config.DefaultSettings,
        "mappings": indexConfig["mappings"]
    }

    es = getClient()
    es.indices.delete(indexName, ignore=404)
    es.indices.create(indexName, indexBody)


def updateInstance(instances, updatedFields, esIndex, esDocType, docMethod, modelClass, prefetchRelations=None):
    instances = instances if isinstance(instances, (list, tuple, set, QuerySet)) else [instances]
    if not instances:
        return

    es = getClient()

    actions = []
    for instance in instances:
        if instance.inactive:
            es.delete(index=esIndex, doc_type=esDocType, id=instance.id, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "update",
                "_index": esIndex,
                "_type": esDocType,
                "_id": instance.id,
                "doc": docMethod(instance, fields=updatedFields)
            })

    if actions:
        try:
            helpers.bulk(es, actions)
        except:
            indexInstance(instances, esIndex, esDocType, docMethod, modelClass=modelClass, prefetchRelations=prefetchRelations)


def indexInstance(instances, esIndex, esDocType, docMethod, modelClass, prefetchRelations=None):
    instances = instances if isinstance(instances, (list, tuple, set, QuerySet)) else [instances]
    if not instances:
        return

    if isinstance(instances[0], int) or isinstance(instances[0], str):
        instances = modelClass.objects.filter(pk__in=instances)
        if prefetchRelations:
            for relation in prefetchRelations:
                instances = instances.prefetch_related(relation)
        instances = instances.all()

    es = getClient()

    actions = []
    for instance in instances:
        if instance.inactive:
            es.delete(index=esIndex, doc_type=esDocType, id=instance.id, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "index",
                "_index": esIndex,
                "_type": esDocType,
                "_id": instance.id,
                "_source": docMethod(instance)
            })

    if actions:
        helpers.bulk(es, actions)


def updateInstanceBranches(instanceBranches, updatedFields, esIndex, esDocType, instanceProp, docMethod, modelClass, prefetchRelations=None):
    instanceBranches = instanceBranches if isinstance(instanceBranches, (list, tuple, set, QuerySet)) else [instanceBranches]
    if not instanceBranches:
        return

    es = getClient()

    actions = []
    for instanceBranch in instanceBranches:
        indexId = "{0}_{1}".format(getattr(instanceBranch, instanceProp + "_id"), instanceBranch.branchKey)
        if instanceBranch.inactive:
            es.delete(index=esIndex, doc_type=esDocType, id=indexId, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "update",
                "_index": esIndex,
                "_type": esDocType,
                "_id": indexId,
                "doc": docMethod(getattr(instanceBranch, instanceProp), branch=instanceBranch, fields=updatedFields)
            })

    if actions:
        try:
            helpers.bulk(es, actions)
        except:
            indexInstanceBranch(instanceBranches, esIndex, esDocType, instanceProp, docMethod, modelClass=modelClass, prefetchRelations=prefetchRelations)


def indexInstanceBranch(instanceBranches, esIndex, esDocType, instanceProp, docMethod, modelClass, prefetchRelations=None):
    instanceBranches = instanceBranches if isinstance(instanceBranches, (list, tuple, set, QuerySet)) else [instanceBranches]
    if not instanceBranches:
        return

    if isinstance(instanceBranches[0], int) or isinstance(instanceBranches[0], str):
        instanceBranches = modelClass.objects.filter(pk__in=instanceBranches).select_related(instanceProp)
        if prefetchRelations:
            for relation in prefetchRelations:
                instanceBranches = instanceBranches.prefetch_related(relation)
            instanceBranches = instanceBranches.all()

    es = getClient()

    actions = []
    for instanceBranch in instanceBranches:
        indexId = "{0}_{1}".format(getattr(instanceBranch, instanceProp + "_id"), instanceBranch.branchKey)
        if instanceBranch.inactive:
            es.delete(index=esIndex, doc_type=esDocType, id=indexId, ignore=404, refresh=True)
        else:
            actions.append({
                "_op_type": "index",
                "_index": esIndex,
                "_type": esDocType,
                "_id": indexId,
                "_source": docMethod(getattr(instanceBranch, instanceProp), branch=instanceBranch)
            })

    if actions:
        helpers.bulk(es, actions)