from pathlib import Path
from datetime import datetime
import sys
sys.path.append('../')
from src.QueryTool import *
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery


def load_query(query_folder):
    query_path = Path(query_folder)
    cq, zq, gq = None, None, None
    for q in query_path.glob('*.xml'):
        if q.stem.endswith('class_queries'):
            cq = ClassQuery(str(q))
        if q.stem.endswith('zerohop_queries'):
            zq = ZerohopQuery(str(q))
        if q.stem.endswith('graph_queries'):
            gq = GraphQuery(str(q))
    return cq, zq, gq


def run_ta1(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki, ta3=False):
    def wrap_output_filename(_doc, _type):
        """
        The responses to queries should be a compressed tarball (.tgz or .zip) of a single directory (named with the run ID),
        with 3 xml response files per document per batch of queries.

        <DocumentID>.<batchNumber>.{class_responses,zerohop_responses,graph_responses}.xml
        (e.g.,  “IC0015PZ4.batch1.class_responses.xml”)
        """
        return '%s%s.batch%s.%s_responses.xml' % (output_folder, _doc, batch_num, _type)

    print('start - ', str(datetime.now()))
    cq, zq, gq = load_query(query_folder)
    ttls = list(Path(ttls_folder).glob('*.ttl'))
    loggers = {
        'class':  open(log_folder + 'class_error.csv', 'w'),
        'zerohop':  open(log_folder + 'zerohop_error.csv', 'w'),
        'graph':  open(log_folder + 'graph_error.csv', 'w'),
    }
    related_graph = open(log_folder + 'related_graph.csv', 'w')
    has_res_graph = open(log_folder + 'has_res_graph.csv', 'w')

    cnt = 0
    total = len(ttls)
    per = min(total // 100, 1)

    for KB in ttls:
        if cnt % per == 0:
            print('\t run %d of %d - ' % (cnt, total), str(datetime.now()))
        cnt += 1
        qt = QueryTool(str(KB), Mode.CLUSTER, relax_num_ep=1, use_fuseki=fuseki or '')

        for query, _type in [
            # (cq, 'class'),
            (zq, 'zerohop'),
            (gq, 'graph')
        ]:
            # print('doc_id: %s, query type: %s' % (KB.stem, _type))
            if ta3:
                response, stat = query.ask_all(qt)
            else:
                response, stat = query.ask_all(qt, root_doc=KB.stem)
            if len(response):
                write_file(response, wrap_output_filename(KB.stem, _type))
            if len(stat['errors']):
                # each error: doc_id,query_id,query_idx,error_str
                loggers[_type].write(stat['errors'])
                loggers[_type].write('\n')
            if stat.get('related') and stat.get('has_res'):
                related_graph.write(','.join(stat.get('related')))
                related_graph.write('\n')
                has_res_graph.write(','.join(stat.get('has_res')))
                has_res_graph.write('\n')

    for v in loggers.values():
        v.close()
    print(' done - ', str(datetime.now()))


def run_ta2(select_endpoint, query_folder, output_folder, log_folder, batch_num):
    def wrap_output_filename(_type):
        """
        The responses to queries should be a compressed tarball (.tgz or .zip) of a single directory (named with the run ID),
        with 3 xml response files per batch of queries.
        Please name your response files TA2.<batchNumber>.
        {class_responses,zerohop_responses,graph_responses}.xml  (e.g.,  “TA2.batch1.class_responses.xml”)
        """
        return '%sTA2.batch%s.%s_responses.xml' % (output_folder, batch_num, _type)

    print('start - ', str(datetime.now()))
    cq, zq, gq = load_query(query_folder)
    loggers = {
        'class':  open(log_folder + 'class_error.csv', 'w'),
        'zerohop':  open(log_folder + 'zerohop_error.csv', 'w'),
        'graph':  open(log_folder + 'graph_error.csv', 'w'),
    }
    qt = QueryTool(select_endpoint, Mode.PROTOTYPE)

    for query, _type in [
        (cq, 'class'),
        (zq, 'zerohop'),
        (gq, 'graph')
    ]:
        # print('doc_id: %s, query type: %s' % (KB.stem, _type))
        response, error = query.ask_all(qt)
        if len(response):
            write_file(response, wrap_output_filename(_type))
        if len(error):
            # each error: doc_id,query_id,query_idx,error_str
            loggers[_type].write(error)
            loggers[_type].write('\n')

    for v in loggers.values():
        v.close()
    print(' done - ', str(datetime.now()))


def run_ta3(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki):
    """
    The responses to queries should be a compressed tarball (.tgz or .gz) of a single directory (named with the run ID),
    containing one subdirectory for each frame ID for each statement of information need; e
    ach of these subdirectories should be named with the frame ID and should contain 3 xml response files per hypothesis.
    Please name your files <hypothesisID>.{class_responses,zerohop_responses,graph_responses}.xml,
    where hypothesisID is the name of the aida:Hypothesis object in your AIF graph.
    """
    run_ta1(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki, ta3=True)


_, param = sys.argv
runs = {
    'ta1': run_ta1,
    'ta2': run_ta2,
    'ta3': run_ta3
}
with open(param) as f:
    params = json.load(f)
    for k, v in params.items():
        if v.get('run'):
            runs[k](**v.get('params'))

