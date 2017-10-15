
def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client["osm"]
    return db

def print_number_of_elements(db):
    print("Number of Elements:\n")
    result = db.bh.find({"data_type":"node"}).count()
    print("  >Number of Nodes: {0}".format(result))
    result = db.bh.find({"data_type":"way"}).count()
    print("  >Number of Ways: {0}".format(result))
    result = db.bh.find({"data_type":"relation"}).count()
    print("  >Number of Relations: {0}".format(result))
    result = db.bh.find().count()
    print("  >Total of elements: {0}".format(result))

def print_main_contibutors(db):
    print("\nTop 10 contributors:\n")
    pipeline = [
        {"$project":{
            "user":"$created.user",
            "total_of_elements": {"$add":1}
        }},
        #{"$group": {"_id":"$data_type", "user":"$created.user", "count":{"$sum":1}}},
        {"$group": {"_id":"$user", "count":{"$sum":1}, "total":{"$max":"$total_of_elements"}}},
#        {"$project":{
#            "user":"$created.user",
#            "count":"$count",
#            "perc": {"$divide":["$count","$total"]}
#        }},
        {"$sort":{"count":-1}},
        {"$limit":10}
    ]
    for user in db.bh.aggregate(pipeline):
        print(user)
        #print("  >User: {0} - contributions: {1}".format(user["_id"], user["count"]))

def print_contibutions_for_period(db):
    print("\nContributios by year:\n")
    pipeline = [
        {"$project":{"year":{"$substr":["$created.timestamp",0,4]},}},
        {"$group": {"_id":"$year", "count":{"$sum":1}}},
        {"$sort":{"count":-1}}
    ]
    for user in db.bh.aggregate(pipeline):
        print(user)
        #print("  >User: {0} - contributions: {1}".format(user["_id"], user["count"]))

def main():
    db = get_db()
    print_number_of_elements(db)
    #print_main_contibutors(db)
    print_contibutions_for_period(db)

if __name__ == "__main__":
    main()