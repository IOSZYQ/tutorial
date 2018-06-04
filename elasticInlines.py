__author__ = "swolfod"

from utilities import djangoUtils


def collectionSearch(branchKey, collection):
    searchChannel = None
    searchBranchKey = branchKey
    searchPublic = True

    if collection == "tos":
        searchChannel = None
        searchBranchKey = None
        searchPublic = True
    elif collection is not None:
        try:
            collection = int(collection)
            if collection:
                searchPublic = False
            else:
                searchBranchKey = None
        except:
            searchChannel = djangoUtils.decodeId(collection)
            searchBranchKey = None
            searchPublic = True

    return searchBranchKey, searchPublic, searchChannel


def filterBranching(filters, public, branchKey):
    if public and not branchKey:
        filters.append({ "term": { "public": True } })
        filters.append({ "term": { "original": True } })
    elif branchKey and not public:
        filters.append({ "term": { "branchKey": branchKey } })
        filters.append({ "term": { "original": False } })
    elif branchKey and public:
        filters.append({
            "bool": {
		        "must_not": { "term" : {"groupBranchKeys": branchKey} },
                "should": [
                    {
                        "bool": {
                            "must": [
                                { "term" : {"original" : True} },
                                { "term" : {"public" : True} }
                            ],
                            "must_not": { "term" : {"branchKey": branchKey} }
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                { "term" : {"original" : False} },
                                { "term" : {"branchKey": branchKey} }
                            ]
                        }
                    }]
                }
            })
    else:
        filters.append({ "term" : {"original" : True} })