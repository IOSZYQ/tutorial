__author__ = 'HanHui'


from elasticsearch import Elasticsearch


DefaultSettings = {
    "index" : {
        "number_of_shards" : 3,
        "number_of_replicas" : 1
    },
    "analysis": {
        "analyzer": {
            "default": {
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_smart",
                "tokenizer": "ik_max_word"
            }
        }
    }
}


Indices = {
    "lushu_hotels": {
        "mappings" : {
            "hotel": {
                "properties" : {
                    "name_en"               : { "type": "string", "term_vector": "with_positions_offsets" },
                    "name_cn"               : { "type": "string", "term_vector": "with_positions_offsets" },
                    "source"                : { "type": "string", "index": "not_analyzed" },
                    "sourceId"              : { "type": "string", "index": "not_analyzed" },
                    "tosId"                 : { "type": "integer" },
                    "cityId"                : { "type": "string", "index": "not_analyzed" },
                    "address"               : { "type": "string", "term_vector": "with_positions_offsets" },
                    "latitude"              : { "type": "float" },
                    "longitude"             : { "type": "float" },
                    "starRating"            : { "type": "float" },
                    "telephone"             : { "type": "string",  "index": "not_analyzed"},
                    "created"               : { "type": "date" },
                }
            }
        }
    }
}
