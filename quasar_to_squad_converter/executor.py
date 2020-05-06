import logging
import argparse
import util as UTIL
import sys
import os
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#from ds_formatter import qangaroo, mctest, insuranceqa, triviaqa, wikiqa, narrativeqa, msmarco, ubuntudialogue, cnnnews, squad, quasar
import quasar

def get_parser():
    try:
        print('inside parser')
        parser = argparse.ArgumentParser()
        print('inside argparse.ArgumentParser()')
        parser.add_argument('--log_path',default="log.txt",help="path to the log file")
        parser.add_argument('--log_info',default="INFO", help="logging level")
        parser.add_argument('--data_path', default=".",help="path to the source file to be converted")
        parser.add_argument('--from_files', 
            default="source:long_dev_questions.json,document:long_dev_contexts.json,nps:long_dev_nps.json, type:t,is_null_tags_filter:true,limit:-1",help="addition/supporting files that are in the same path as source, could be coma-seperated ',', file type can be also identified with ':'. Ex: 'voc:vocabulary.txt, 'answer:answer.txt'")
        parser.add_argument('--from_format', default="quasar-t",help="dataset name of the source format")
        parser.add_argument('--to_format', default="squad",help="dataset name of the destination format")
        parser.add_argument('--to_file_name', default="long_dev_out.json",help="destination file name")
        print('print parser', parser)
    except Exception as e:
        logging.error('Issues')
        print('print parser issues', parser)
        raise
    return parser

def main(args):
    try:
        print('in Main', args)
        print(args.from_format.lower(), args.to_format.lower())
        logging.info('(function {}) Started'.format(main.__name__))

        source_files = UTIL.parse_source_files(args.data_path, args.from_files, logging)
        source_file = source_files['source']
        destination_file = os.path.join(args.data_path, args.from_format.lower() + '_to_' + args.to_format.lower() + '_'+args.to_file_name)

        # TODO: 1) We need to create a interface class to have the same signature for all the formatters in ds_formatter folder.
        # TODO: 2) We need to create a generic approach to convert any type to any type not only any type to squad.
        # TODO: 3) can we have better approach to handle the following if/else scenarios
        # TODO: 4) we may also put some kind of field wrapper to handle whether which fields are gonna be filled with dummy and which fields are gonna be filled with real values.
           
        if args.from_format.lower() == 'quasar-t' and args.to_format.lower() == 'squad':
            """            
            --log_path="~/log.log" 
            --data_path="~/data/quasar-t"
            --from_format="quasar-t" 
            --to_format="squad"
            --from_files="source:train_questions.json,document:train_contexts.json,type:t,is_null_tags_filter:true, limit:-1"
            --to_file_name="train.json"
            """
            print('in quasar')
            if source_files['type'].lower() =='t':
                # quasar-t
                queries = UTIL.load_json_line_file(source_file, logging)
                documents = UTIL.load_json_line_file(source_files['document'], logging)
                nps = UTIL.load_json_line_file(source_files['nps'], logging)
                formatted_content = quasar.convert_to_squad(queries, 
                                                            documents, 
                                                            nps,
                                                            source_files['is_null_tags_filter'], 
                                                            int(source_files['limit']))
            UTIL.dump_json_file(destination_file, formatted_content, logging)

        else:
            pass
        logging.info('(function {}) Finished'.format(main.__name__))
    except Exception as e:
        logging.error('(function {}) has an error: {}'.format(main.__name__, e))
        raise
if __name__ == '__main__':
    print('Starting')
    try:
        ret = get_parser()
        print('ret = ', ret)
        args = ret.parse_args()
        print('args = ', args)
    except Exception as e:
        print("error in parsing")
        raise
    print('get_parser().parse_args()', args.log_path)
    assert args.log_path is not None, "No log path found at {}".format(args.log_path)
    assert args.data_path is not None, "No folder path found at {}".format(args.data_path)
    assert args.from_format is not None, "No 'from format' found {}".format(args.from_format)
    assert args.from_files is not None, "No 'from files' format found {}".format(args.from_files)
    assert args.to_format is not None, "No 'to format' dataset format found {}".format(
        args.to_format)
    assert args.to_file_name is not None, "No 'to file name' dataset format found {}".format(
        args.to_file_name)

    if args.log_info.lower() =='info':
        log_info = logging.INFO
    elif args.log_info.lower() == 'debug':
        log_info = logging.DEBUG
    elif args.log_info.lower() == 'warn':
        log_info = logging.WARNING
    elif args.log_info.lower() == 'critical':
        log_info = logging.CRITICAL
    elif args.log_info.lower() == 'error':
        log_info = logging.ERROR
    else:
        log_info = logging.INFO

    logging.basicConfig(filename=args.log_path, level=log_info)
    print('logging.basicConfig')
    main(args)