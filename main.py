import config as cfg
import json
from vision import Vision
from dpconfig_parser import DataParser
from dpconfig_mapper import DataMapper
import urllib3
import logging_helper
import sys
import os


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#Arguments variables

getdatafromvision = True
email = False
test_email_alarm = False
report = []

raw_data_path = "./Raw Data/"

if not os.path.exists('log'):
	os.makedirs('log')

if not os.path.exists('Raw Data'):
	os.makedirs('Raw Data')

if not os.path.exists('Reports'):
	os.makedirs('Reports')

if not os.path.exists('Config'):
	os.makedirs('Config')

logging_helper.log_setup(cfg.LOG_FILE_PATH, cfg.SYSLOG_SERVER, cfg.SYSLOG_PORT)


for i in sys.argv:
	#Running script with arguments

	if i.lower() == "--use-cache-data":
		#No data collection from vision- running script using previously collected data
		getdatafromvision = False
		logging_helper.logging.info('Running script using cache data only')
		print('Running script using cache data only')
		
	if i.lower() == "--email":
		#Run script and send report by email.
		email = True
		logging_helper.logging.info('Running script with sending email argument')
		print('Running script with sending email argument')

	if i.lower() == "--test-email":
		#Run script- test sending email only
		logging_helper.logging.info('Running script with test email argument')
		print('Running script with test email argument')
		getdatafromvision = False
		test_email_alarm = True
		nobdosreport = True
		nodpconfigparsing = True


if not getdatafromvision:

	with open(raw_data_path + 'full_pol_dic.json') as full_pol_dic_file:
		full_pol_dic = json.load(full_pol_dic_file)

	with open(raw_data_path + 'full_sig_dic.json') as full_sig_dic_file:
		full_sig_dic = json.load(full_sig_dic_file)

	with open(raw_data_path + 'full_net_dic.json') as full_net_dic_file:
		full_net_dic = json.load(full_net_dic_file)

	with open(raw_data_path + 'full_bdosprofconf_dic.json') as full_bdosprofconf_dic_file:
		full_bdosprofconf_dic = json.load(full_bdosprofconf_dic_file)

	with open(raw_data_path + 'full_dnsprofconf_dic.json') as full_dnsprofconf_dic_file:
		full_dnsprofconf_dic = json.load(full_dnsprofconf_dic_file)

	with open(raw_data_path + 'full_synprofconf_dic.json') as full_synprofconf_dic_file:
		full_synprofconf_dic = json.load(full_synprofconf_dic_file)

	with open(raw_data_path + 'full_connlimprofconf_dic.json') as full_connlimprofconf_file:
		full_connlimprofconf_dic = json.load(full_connlimprofconf_file)


if getdatafromvision:
	v = Vision(cfg.VISION_IP, cfg.VISION_USER, cfg.VISION_PASS)
	
	print('Collecting policies data from all DefensePro')
	logging_helper.logging.info('Collecting policies data from all DefensePro')
	full_pol_dic = v.getFullPolicyDictionary()

	print('Collecting signature profiles data from all DefensePro')
	logging_helper.logging.info('Collecting signature profiles data from all DefensePro')
	full_sig_dic = v.getFullSignatureProfileDictionary()

	print('Collecting network classes data from all DefensePro')
	logging_helper.logging.info('Collecting network classes data from all DefensePro')
	full_net_dic = v.getFullNetClassDictionary()

	print('Collecting BDOS configuration data from all DefensePro')
	logging_helper.logging.info('Collecting BDOS configuration data from all DefensePro')
	full_bdosprofconf_dic = v.getFullBDOSProfConfigDictionary()

	print('Collecting DNS configuration data from all DefensePro')
	logging_helper.logging.info('Collecting DNS configuration data from all DefensePro')
	full_dnsprofconf_dic = v.getFullDNSProfConfigDictionary()

	print('Collecting SynFlood configuration data from all DefensePro')
	logging_helper.logging.info('Collecting SynFlood configuration data from all DefensePro')
	full_synprofconf_dic = v.getFullSYNPConfigDictionary()

	print('Collecting Connection Limit configuration data from all DefensePro')
	logging_helper.logging.info('Collecting Connection Limit configuration data from all DefensePro')
	full_connlimprofconf_dic = v.getFullConnlimConfigDictionary()

	print('Downloading DefensePro configuration files')
	logging_helper.logging.info('Downloading DefensePro configuration files')
	v.getAllDPConfigs()

	print('Data collection is complete')
	logging_helper.logging.info('Data collection is complete')

print('Starting data parsing')
logging_helper.logging.info('Starting data parsing')
report.append(DataParser(full_pol_dic,full_sig_dic,full_net_dic,full_bdosprofconf_dic,full_synprofconf_dic).run())

if cfg.MAP_CONFIG:
	print('Starting config mapping')
	report.append(DataMapper(full_pol_dic,full_sig_dic,full_net_dic,full_bdosprofconf_dic,full_dnsprofconf_dic,full_synprofconf_dic,full_connlimprofconf_dic).run())
	
if test_email_alarm:
	report = ['test']

if email:
	logging_helper.send_report(report)