import os, sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.basic.XMLLoader import XMLLoader

# ENDPOINT = 'http://gaiadev01.isi.edu:3030/run1/query'
# ENDPOINT = 'http://gaiadev01.isi.edu:7200/repositories/run1_clean'
ENDPOINT = 'http://localhost:3030/run1dir00/query'


def run(xml_query, output='outputs/'):
    with open(xml_query) as f:
        xml = f.read()

    loader = XMLLoader(xml)
    # while loader.has_next:
    for i in range(min(loader.question_list_length, 3)):
        sparql, responses = loader.answer_next(ENDPOINT)
        print(sparql)

    output_file = output + xml_query.rsplit('/',1)[-1]
    loader.dump_responses(output_file)
        # dump_responses
        # with open(, 'a') as f:
        #     # f.write(sparql)
        #     # f.write('\n')
        #     for response in responses:
        #         # print(response)
        #         f.write(response)
        #         f.write('\n')
        #     f.write('\n')



# run('outputs/autogenerated_query_0.xml')


# run('../resources/version1.3/loop_Q2_H1/graph_query/graph_query.xml')

# run('../resources/version1.3/loop_Q2_H1/zerohop_query/zerohop_query.xml')

run('sample_queries/class_query.xml')
# run('sample_queries/zerohop_query.xml')
# run('sample_queries/graph_query.xml')
