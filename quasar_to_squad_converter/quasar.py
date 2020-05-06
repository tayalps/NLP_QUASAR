import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.utils import shuffle

def convert_to_squad(queries, documents, nps, is_null_tags_filter, limit):
    squad_formatted_content = dict()
    squad_formatted_content['version'] = 'quasar-t_squad_format'
    data=[]
    pairs = create_pairs(zip(queries, documents, nps), is_null_tags_filter)
    # if limit != -1:
    #     pairs = shuffle(pairs)

    pairs = pairs.groupby(['p_id', 'p_content'])
    print (pairs)
    iterator =  tqdm(enumerate(pairs))
    for i, pack in iterator:
        if limit != -1 and i > limit:
            print('Data is prepared at the index of {}'.format(i))
            iterator.close()
            break
        #print ('pack = ', len(pack))
        p, qs = pack[0], pack[1]
        #print(p)
        data_ELEMENT = dict()
        data_ELEMENT['title'] = 'dummyTitle_' + str(i)
        paragraphs = []
        paragraphs_ELEMENT = dict()
        superdocument = p[1]
        paragraphs_ELEMENT['context'] = superdocument
        qas = []
        for q in qs.itertuples():
            #print('len of q', len(q), q)
            _q_indx, _q = q.q_id, q.q_content
            qas_ELEMENT = dict()
            ANSWERS_ELEMENT = dict()
            qas_ELEMENT_ANSWERS = []
            qas_ELEMENT['id'] = _q_indx
            qas_ELEMENT['question'] = _q
            
            for i in range(len(q.p_ans_start)):
                #print(i, q.p_ans_start)
                ANSWERS_ELEMENT = dict()
                ANSWERS_ELEMENT['answer_start']= q.p_ans_start[i]
                ANSWERS_ELEMENT['text']        = q.p_ans[i]
                qas_ELEMENT_ANSWERS.append(ANSWERS_ELEMENT)
            #ANSWERS_ELEMENT['answer_start'] = q.p_ans_start
            #ANSWERS_ELEMENT['text'] = q.p_ans
            #qas_ELEMENT_ANSWERS.append(ANSWERS_ELEMENT)
            qas_ELEMENT['answers'] = qas_ELEMENT_ANSWERS
            #print(qas_ELEMENT['answers'])
            qas.append(qas_ELEMENT)
        paragraphs_ELEMENT['qas'] = qas
        paragraphs.append(paragraphs_ELEMENT)

        data_ELEMENT['paragraphs'] = paragraphs
        data.append(data_ELEMENT)
    squad_formatted_content['data'] = data
    return squad_formatted_content

def create_pairs(query_document_pair, is_null_tags_filter):
    pairs = []
    generator = enumerate(query_document_pair)
    for i, pair in generator:
        query, context, nps = pair[0], pair[1], pair[2]
        if is_null_tags_filter.lower() in ['true', 'True', 'TRUE']:
            if len(query['tags']) == 0:
                continue
        if query['uid'] != context['uid']:
            print(20 * '!')
            print('Query {} - Document {} is mismatched.'.format(query['uid'],context['uid']))
        
        assert query['uid'] == context['uid']
        assert query['uid'] == nps['uid']
        assert nps['uid'] == context['uid']
        
        ans = query['answer']
        print('ans = ',  ans, len(context['contexts']))
        for ctx_counter in range(len(context['contexts'])):#len(context['contexts'][0])):
            
            ids = [i for i, c in enumerate(nps['nps']) if (
                    (c[1]==ctx_counter) & (c[0].lower()==ans) )]
            subsetnps = [nps['nps'][i] for i in ids ]
            
            #for every_candid in subsetnps:
            answerlist = [c[0] for c in subsetnps]
            answerstartlist = [c[2] for c in subsetnps]
            if (len(answerlist) > 0):
                pairs.append([query['uid'], 
                              query['question'], 
                              i, 
                              context['contexts'][ctx_counter][1],
                              answerlist, #every_candid[0], # answer 
                              answerstartlist])#every_candid[2]]) # answer start
            #print (ctx_counter)
            #print (pairs)
            #break
    return pd.DataFrame(pairs, 
                        columns=['q_id', 
                                 'q_content', 
                                 'p_id', 
                                 'p_content',
                                 'p_ans',
                                 'p_ans_start'])
