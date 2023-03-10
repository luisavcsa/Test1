import config as cfg
import csv
import logging_helper


reports_path = cfg.REPORTS_PATH

class DataMapper():
	def __init__(self, full_pol_dic, full_sig_dic, full_net_dic, full_bdosprofconf_dic, full_dnsprofconf_dic, full_synprofconf_dic, full_connlimprofconf_dic):
		self.full_pol_dic = full_pol_dic
		self.full_sig_dic = full_sig_dic
		self.full_net_dic = full_net_dic
		self.full_bdosprofconf_dic = full_bdosprofconf_dic
		self.full_dnsprofconf_dic = full_dnsprofconf_dic
		self.full_synprofconf_dic = full_synprofconf_dic
		self.full_connlimprofconf_dic = full_connlimprofconf_dic
		self.na_list = ['']

		with open(reports_path + 'dpconfig_map.csv', mode='w', newline="") as dpconfigmap_report:
			dp_configmap_writer = csv.writer(dpconfigmap_report, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			dp_configmap_writer.writerow(['DefensePro Name' , 'DefensePro IP' ,	'DefensePro Version' , 'Policy Name','Policy Block/Report', 'Policy Packet Reporting','Signature Profile Name','Out of State Profile Name','Anti-Scanning Profile Name', 'EAAF Profile Name','Geolocaation Profile','Connection Limit Profile Name','Connection Limit Profile Protections and settings','SYN Flood Protection Profile','SYN Flood Profile Action','SYN Flood Network Authentication Method', 'SYN Flood HTTP Authentication','SYN Flood Protection Settings','Traffic Filter Profile Name','BDOS Profile Name','BDOS Profile Block/Report','BDOS Profile Bandwidth','BDOS TCP Quota','BDOS UDP Quota','BDOS ICMP Quota','BDOS Transparent Optimization','BDOS Packet Reporting','BDOS Learning Suppression','BDOS Footprint Strictness','BDOS UDP Packet Rate Detection Sensitivity','BDOS Burst-Attack Protection','DNS Profile Name','DNS Block/Report','DNS Expected QPS','DNS Max Allowed QPS','DNS A Status','DNS A Quota','DNS MX Status','DNS MX Quota','DNS PTR Status','DNS PTR Quota','DNS AAAA Status','DNS AAAA Quota','DNS Text Status','DNS Text Quota','DNS SOA Status','DNS SOA Quota','DNS Naptr Status','DNS Naptr Quota','DNS SRV Status','DNS SRV Quota','DNS Other Status','DNS Other Quota','DNS Packet Reporting','DNS Learning Suppression','DNS Footprint Strictness'])

	def isDPAvailable(self, dp_ip,dp_attr):
		# DP is considerd unavailable if DP is unreachable or no policy exists

		try:
			if not dp_attr['Policies']:
				print(f'{dp_ip} is not unavailable')
				return False
		except:
			pass

		try:
			if dp_attr['Policies'] == None:
				print(f'{dp_ip} is not unavailable')
				return False
		except:
			pass

		try:	
			if not dp_attr['Profiles']:
				print(f'{dp_ip} is not unavailable')
				return False
		except:
			pass

		return True


	def map_synp_profile(self,dp_ip,pol_synp_prof_name):
		#This function maps the bdos profiles to dpconfig_map.csv
		synp_settings = []
		synp_prot_values = ''

		if pol_synp_prof_name == "": # If SYNP profile is not configured, pad all bdos fields with N/A values
			synp_settings.append('')
			synp_settings = synp_settings + self.na_list *4
			
		else:
			for synp_dp_ip, synp_dp_attr in self.full_synprofconf_dic.items():

				if synp_dp_attr['Profiles']:
					for synp_prof_key, syn_prof_val in synp_dp_attr['Profiles'].items():
						synp_prof_name = synp_prof_key

						if dp_ip == synp_dp_ip and pol_synp_prof_name == synp_prof_name:

							synp_settings.append(synp_prof_name) # Append SYN Flood Protection Profile Name
							


							############# SYN Flood Protection Action Block/Report #############

							if 'rsIDSSynProfilesAction' in syn_prof_val['Parameters']:
								if syn_prof_val['Parameters']['rsIDSSynProfilesAction'] == '0':
										synp_settings.append('Report Only')
								elif syn_prof_val['Parameters']['rsIDSSynProfilesAction'] == '1':
									synp_settings.append('Block and Report')

							else:
								synp_settings.append('N/A in this version')



							############# SYN Flood Protection Authentication Method: #############

							if 'rsIDSSynProfilesParamsAuthType' in syn_prof_val['Parameters']:
								if syn_prof_val['Parameters']['rsIDSSynProfilesParamsAuthType'] == '1':
									if syn_prof_val['Parameters']['rsIDSSynProfileTCPResetStatus'] == '2':
										synp_settings.append('Safe Reset /Disabled "Use TCP Reset for Supported Protocols"')
									elif syn_prof_val['Parameters']['rsIDSSynProfileTCPResetStatus'] == '1':
										synp_settings.append('Safe Reset /Enabled "Use TCP Reset for Supported Protocols"')

								elif syn_prof_val['Parameters']['rsIDSSynProfilesParamsAuthType'] == '2':
									synp_settings.append('Transparent Proxy')

							else:
								synp_settings.append('N/A in this version')

							############# SYN Flood Protection Application Level Authentication #############

							if 'rsIDSSynProfilesParamsWebEnable' in syn_prof_val['Parameters']:
								if syn_prof_val['Parameters']['rsIDSSynProfilesParamsWebEnable'] == '1':
									if syn_prof_val['Parameters']['rsIDSSynProfilesParamsWebMethod'] == '1':
										synp_settings.append('Use HTTP Authentication with 302-Redirect')

									elif syn_prof_val['Parameters']['rsIDSSynProfilesParamsWebMethod'] == '2':
										synp_settings.append('Use HTTP Authentication with JavaScript')

									elif syn_prof_val['Parameters']['rsIDSSynProfilesParamsWebMethod'] == '3':
										synp_settings.append('Use HTTP Authentication with Advanced JavaScript')

								elif syn_prof_val['Parameters']['rsIDSSynProfilesParamsWebEnable'] == '2':
									synp_settings.append('Disabled')

							else:
								synp_settings.append('N/A in this version')
								

							############# SYN Flood Protection Settings #############
							
							for synp_prof_prot in syn_prof_val['Protections']:

								synp_prot_values = synp_prot_values + f'Protection Name: {synp_prof_prot["rsIDSSYNAttackName"]}\r\nProtection ID: {synp_prof_prot["rsIDSSYNAttackId"]}\r\nApplication Port Group: {synp_prof_prot["rsIDSSYNDestinationAppPortGroup"]}\r\nActivation Threshold: {synp_prof_prot["rsIDSSYNAttackActivationThreshold"]}\r\nTermination Threshold: {synp_prof_prot["rsIDSSYNAttackTerminationThreshold"]}\r\n------\r\n'

							synp_settings.append(synp_prot_values)

		return synp_settings


	def map_connlim_profile(self,dp_ip,pol_connlim_prof_name):
		#This function maps the bdos profiles to dpconfig_map.csv
		connlim_settings = [] #this will go to csv report
		connlim_prot_values = ''

		if pol_connlim_prof_name == "": # If Connection Limit profile is not configured, pad all bdos fields with N/A values
			connlim_settings.append('')
			connlim_settings = connlim_settings + self.na_list
			
		else:
			for connlim_dp_ip, connlim_dp_attr in self.full_connlimprofconf_dic.items():

				if connlim_dp_attr['Profiles']:
					for connlim_prof_key, connlim_prof_val in connlim_dp_attr['Profiles'].items():
						connlim_prof_name = connlim_prof_key

						if dp_ip == connlim_dp_ip and pol_connlim_prof_name == connlim_prof_name:

							connlim_settings.append(connlim_prof_name) # Append Connection limit Protection Profile Name
							

							############# Connection limit Protections Settings #############
							
							for connlim_prof_prot in connlim_prof_val['Protections']:

								if connlim_prof_prot['rsIDSConnectionLimitAttackType']:
									if connlim_prof_prot['rsIDSConnectionLimitAttackType'] == '1':
										connlim_type = 'Connections per Second'
									if connlim_prof_prot['rsIDSConnectionLimitAttackType'] == '2':
										connlim_type = 'Concurrent Connections'


								if connlim_prof_prot['rsIDSConnectionLimitAttackPacketReport']:
									if connlim_prof_prot['rsIDSConnectionLimitAttackPacketReport'] == '1':
										connlim_reporting = 'Enabled'
									if connlim_prof_prot['rsIDSConnectionLimitAttackPacketReport'] == '2':
										connlim_reporting = 'Disabled'


								if connlim_prof_prot['rsIDSConnectionLimitAttackProtocol']:
									if connlim_prof_prot['rsIDSConnectionLimitAttackProtocol'] == '2':
										connlim_protoctol = 'TCP'
									elif connlim_prof_prot['rsIDSConnectionLimitAttackProtocol'] == '3':
										connlim_protoctol = 'UDP'

								if connlim_prof_prot['rsIDSConnectionLimitAttackTrackingType']:

									if connlim_prof_prot['rsIDSConnectionLimitAttackTrackingType'] == '2':
										connlim_tracking_type = 'Source Count'
									elif connlim_prof_prot['rsIDSConnectionLimitAttackTrackingType'] == '3':
										connlim_tracking_type = 'Destination Count'
									elif connlim_prof_prot['rsIDSConnectionLimitAttackTrackingType'] == '4':
										connlim_tracking_type = 'Source and Destination Count'
									elif connlim_prof_prot['rsIDSConnectionLimitAttackTrackingType'] == '5':
										connlim_tracking_type = 'Count by Destination IP Address and Port'
								if connlim_prof_prot["rsIDSConnectionLimitAttackReportMode"]:
									if connlim_prof_prot["rsIDSConnectionLimitAttackReportMode"] == '0':
										connlim_action = 'Report Only'
									elif connlim_prof_prot["rsIDSConnectionLimitAttackReportMode"] == '10':
										connlim_action = 'Drop'

								connlim_prot_values = connlim_prot_values + f'Protection Name: {connlim_prof_prot["rsIDSConnectionLimitAttackName"]}\r\nProtection ID: {connlim_prof_prot["rsIDSConnectionLimitAttackId"]}\r\nProtection Type: {connlim_type}\r\nProtocol: {connlim_protoctol}\r\nThreshold: {connlim_prof_prot["rsIDSConnectionLimitAttackThreshold"]}\r\nTracking Type: {connlim_tracking_type}\r\nAction: {connlim_action}\r\nPacket Reporting: {connlim_reporting}\r\n------\r\n'

							connlim_settings.append(connlim_prot_values)
		return connlim_settings


	def map_bdos_profile(self,dp_ip,pol_bdos_prof_name):
		#This function maps the bdos profiles to dpconfig_map.csv
		bdos_settings = []

		if pol_bdos_prof_name == "": # If BDOS profile is not configured, pad all bdos fields with N/A values
			bdos_settings.append('')
			bdos_settings = bdos_settings + self.na_list *11
			

		for bdos_dp_ip, bdos_dp_attr in self.full_bdosprofconf_dic.items():

			if bdos_dp_attr['Policies']:
				for bdos_prof in bdos_dp_attr['Policies']['rsNetFloodProfileTable']:
					bdos_prof_name = bdos_prof['rsNetFloodProfileName']
					
					if dp_ip == bdos_dp_ip and pol_bdos_prof_name == bdos_prof_name:
						bdos_settings.append(bdos_prof_name)
						
						########## Block/Report check#########
						if 'rsNetFloodProfileAction' in bdos_prof:
							if bdos_prof['rsNetFloodProfileAction'] == '0':
								bdos_settings.append('Report')
							elif bdos_prof['rsNetFloodProfileAction'] == '1':
								bdos_settings.append('Block and Report')
							
						else:
							bdos_settings.append('N/A in this version')
						########## Map BDOS Bandwidth and Quota #########
						bdos_settings.append(bdos_prof['rsNetFloodProfileBandwidthIn']) # Bandwidth
						bdos_settings.append(bdos_prof['rsNetFloodProfileTcpInQuota'])
						bdos_settings.append(bdos_prof['rsNetFloodProfileUdpInQuota'])
						bdos_settings.append(bdos_prof['rsNetFloodProfileIcmpInQuota'])

						########## BDOS Transparent optimization check#########
						if 'rsNetFloodProfileTransparentOptimization' in bdos_prof:
							if bdos_prof['rsNetFloodProfileTransparentOptimization'] == '1':
								bdos_settings.append('Enabled')
							if bdos_prof['rsNetFloodProfileTransparentOptimization'] == '2':
								bdos_settings.append('Disabled')
						else:
							bdos_settings.append('N/A in this version')
						#####################################


						########## BDOS Packet reporting check#########
						if 'rsNetFloodProfilePacketReportStatus' in bdos_prof:
							if bdos_prof['rsNetFloodProfilePacketReportStatus'] == '1':
								bdos_settings.append('Enabled')
							if bdos_prof['rsNetFloodProfilePacketReportStatus'] == '2':
								bdos_settings.append('Disabled')
						else:
							bdos_settings.append('N/A in this version')
						#####################################

						########## BDOS Learning Suppression mapping #########
						if 'rsNetFloodProfileLearningSuppressionThreshold' in bdos_prof:
							bdos_settings.append(bdos_prof['rsNetFloodProfileLearningSuppressionThreshold'])
						else:
							bdos_settings.append('N/A in this version')

						########## BDOS Footprint Strictness #########
						if 'rsNetFloodProfileFootprintStrictness' in bdos_prof:
							if bdos_prof['rsNetFloodProfileFootprintStrictness'] == '0':
								bdos_settings.append('Low')
							if bdos_prof['rsNetFloodProfileFootprintStrictness'] == '1':
								bdos_settings.append('Medium')
							if bdos_prof['rsNetFloodProfileFootprintStrictness'] == '2':
								bdos_settings.append('High')
						else:
							bdos_settings.append('N/A in this version')
						#####################################

						########## BDOS UDP Packet Rate Detection Sensitivity #########
						if 'rsNetFloodProfileLevelOfReuglarzation' in bdos_prof:
							if bdos_prof['rsNetFloodProfileLevelOfReuglarzation'] == '1':
								bdos_settings.append('Ignore or Disable')
							if bdos_prof['rsNetFloodProfileLevelOfReuglarzation'] == '2':
								bdos_settings.append('Low')
							if bdos_prof['rsNetFloodProfileLevelOfReuglarzation'] == '3':
								bdos_settings.append('Medium')
							if bdos_prof['rsNetFloodProfileLevelOfReuglarzation'] == '4':
								bdos_settings.append('High')
						else:
							bdos_settings.append('N/A in this version')
						#####################################

						########## BDOS Burst-Attack Protection #########
						if 'rsNetFloodProfileBurstEnabled' in bdos_prof:
							if bdos_prof['rsNetFloodProfileBurstEnabled'] == '1':
								bdos_settings.append('Enabled')
							if bdos_prof['rsNetFloodProfileBurstEnabled'] == '2':
								bdos_settings.append('Disabled')
						else:
							bdos_settings.append('N/A in this version')

		return bdos_settings


	def map_dns_profile(self,dp_ip,pol_dns_prof_name):
		#This function maps the bdos profiles to dpconfig_map.csv
		dns_settings = []
		

		if pol_dns_prof_name == "" or pol_dns_prof_name == "null":
			dns_settings.append('')
			
			dns_settings = dns_settings + self.na_list *24



		for dns_dp_ip, dns_dp_attr in self.full_dnsprofconf_dic.items():

			if dns_dp_attr['Policies']:
				for dns_prof in dns_dp_attr['Policies']['rsDnsProtProfileTable']:
					dns_prof_name = dns_prof['rsDnsProtProfileName']
					
					if dp_ip == dns_dp_ip and pol_dns_prof_name == dns_prof_name:
						dns_settings.append(dns_prof_name)
						
						########## DNS Block/Report check#########
						if 'rsDnsProtProfileAction' in dns_prof:
							if dns_prof['rsDnsProtProfileAction'] == '0':
								dns_settings.append('Report')
							elif dns_prof['rsDnsProtProfileAction'] == '1':
								dns_settings.append('Block and Report')
							
						else:
							dns_settings.append('N/A in this version')


						########## Map DNS QPS and Quota #########
						dns_settings.append(dns_prof['rsDnsProtProfileExpectedQps']) # Bandwidth
						dns_settings.append(dns_prof['rsDnsProtProfileMaxAllowQps'])

						if dns_prof['rsDnsProtProfileDnsAStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsAStatus'] == '2':
							dns_settings.append('Disabled')

						dns_settings.append(dns_prof['rsDnsProtProfileDnsAQuota'])


						if dns_prof['rsDnsProtProfileDnsMxStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsMxStatus'] == '2':
							dns_settings.append('Disabled')

						dns_settings.append(dns_prof['rsDnsProtProfileDnsMxQuota'])


						if dns_prof['rsDnsProtProfileDnsPtrStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsPtrStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsPtrQuota'])

						if dns_prof['rsDnsProtProfileDnsAaaaStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsAaaaStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsAaaaQuota'])

						if dns_prof['rsDnsProtProfileDnsTextStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsTextStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsTextQuota'])

						if dns_prof['rsDnsProtProfileDnsSoaStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsSoaStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsSoaQuota'])

						if dns_prof['rsDnsProtProfileDnsNaptrStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsNaptrStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsNaptrQuota'])

						if dns_prof['rsDnsProtProfileDnsSrvStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsSrvStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsSrvQuota'])

						if dns_prof['rsDnsProtProfileDnsOtherStatus'] == '1':
							dns_settings.append('Enabled')
						elif dns_prof['rsDnsProtProfileDnsOtherStatus'] == '2':
							dns_settings.append('Disabled')
						dns_settings.append(dns_prof['rsDnsProtProfileDnsOtherQuota'])


						########## DNS Packet reporting check#########
						if 'rsDnsProtProfilePacketReportStatus' in dns_prof:
							if dns_prof['rsDnsProtProfilePacketReportStatus'] == '1':
								dns_settings.append('Enabled')
							if dns_prof['rsDnsProtProfilePacketReportStatus'] == '2':
								dns_settings.append('Disabled')
						else:
							dns_settings.append('N/A')
						#####################################

						########## DNS Learning Suppression mapping #########
						if 'rsDnsProtProfileLearningSuppressionThreshold' in dns_prof:
							dns_settings.append(dns_prof['rsDnsProtProfileLearningSuppressionThreshold'])
						else:
							dns_settings.append('N/A in this version')

						########## DNS Footprint Strictness #########
						if 'rsDnsProtProfileFootprintStrictness' in dns_prof:
							if dns_prof['rsDnsProtProfileFootprintStrictness'] == '0':
								dns_settings.append('Low')
							if dns_prof['rsDnsProtProfileFootprintStrictness'] == '1':
								dns_settings.append('Medium')
							if dns_prof['rsDnsProtProfileFootprintStrictness'] == '2':
								dns_settings.append('High')
						else:
							dns_settings.append('N/A in this version')
						#####################################

		return dns_settings	



			


	def map_policy(self,dp_name,dp_ver,dp_ip,pol_name,policy):
		policy_settings = [] # this list will go to the csv file
		policy_settings.append(dp_name)
		policy_settings.append(dp_ip)
		policy_settings.append(dp_ver)
		policy_settings.append(pol_name)

		if 'rsIDSNewRulesAction' in policy: # Check policy block/report action
			if policy['rsIDSNewRulesAction'] == '0':
				policy_settings.append('Report')
			elif policy['rsIDSNewRulesAction'] == '1':
				policy_settings.append('Block and Report')

		else:
			policy_settings.append('N/A')

		if 'rsIDSNewRulesPacketReportingStatus'	in policy: # Check packet reporting enabled/Disabled
			if policy['rsIDSNewRulesPacketReportingStatus'] == '1':
				policy_settings.append('Enabled')
			elif policy['rsIDSNewRulesPacketReportingStatus'] == '2':
				policy_settings.append('Disabled')
		else:
			policy_settings.append('N/A in this version')

		############Mapping Signature Profile##########
		if 'rsIDSNewRulesProfileAppsec' in policy: # Check if BDOS profile is configured
			pol_sig_prof_name = policy['rsIDSNewRulesProfileAppsec']

			if pol_sig_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_sig_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################

		############Mapping Out of State Profile##########
		if 'rsIDSNewRulesProfileStateful' in policy: # Check if OOS profile is configured
			pol_oos_prof_name = policy['rsIDSNewRulesProfileStateful']

			if pol_oos_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_oos_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################

		############Mapping Anti-Scanning Profile##########
		if 'rsIDSNewRulesProfileScanning' in policy: # Check if AS profile is configured
			pol_as_prof_name = policy['rsIDSNewRulesProfileScanning']

			if pol_as_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_as_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################

		############Mapping ERT Active Attackers Feed Profile##########
		if 'rsIDSNewRulesProfileErtAttackersFeed' in policy: # Check if ERT Active Attackers Feed profile is configured
			pol_eaaf_prof_name = policy['rsIDSNewRulesProfileErtAttackersFeed']

			if pol_eaaf_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_eaaf_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################

		############Mapping Geolocation  Feed Profile##########
		if 'rsIDSNewRulesProfileGeoFeed' in policy: # Check if Geolocation  profile is configured
			pol_geo_prof_name = policy['rsIDSNewRulesProfileGeoFeed']

			if pol_geo_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_geo_prof_name)

		else:
			policy_settings.append('N/A in this version')
		######################################################


		############Mapping Connection Limit Protection Profile##########
		if 'rsIDSNewRulesProfileConlmt' in policy: # Check if Connection Limit  profile is configured
			pol_connlim_prof_name = policy['rsIDSNewRulesProfileConlmt']
			policy_settings = policy_settings + self.map_connlim_profile(dp_ip,pol_connlim_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################

		############Mapping SYN Flood Protection Profile##########
		if 'rsIDSNewRulesProfileSynprotection' in policy: # Check if SYN Flood Protection profile is configured
			pol_synp_prof_name = policy['rsIDSNewRulesProfileSynprotection']
			policy_settings = policy_settings + self.map_synp_profile(dp_ip,pol_synp_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################


		############Mapping Traffic Filter Profile##########
		if 'rsIDSNewRulesProfileTrafficFilters' in policy: # Check if Tfaffic Filter profile is configured
			pol_tf_prof_name = policy['rsIDSNewRulesProfileTrafficFilters']

			if pol_tf_prof_name == "":
				policy_settings.append('')
			else:
				policy_settings.append(pol_tf_prof_name)

		else:
			policy_settings.append('N/A in this version')
		###############################################


		############Mapping BDOS Profile################
		if 'rsIDSNewRulesProfileNetflood' in policy: # Check if BDOS profile is configured
			pol_bdos_prof_name = policy['rsIDSNewRulesProfileNetflood']
			policy_settings = policy_settings + self.map_bdos_profile(dp_ip,pol_bdos_prof_name)
				
		else:
			policy_settings.append('N/A')
		###############################################



		############Mapping DNS Profile################
		if 'rsIDSNewRulesProfileDNS' in policy: # Check if BDOS profile is configured
			pol_dns_prof_name = policy['rsIDSNewRulesProfileDNS']
			policy_settings = policy_settings + self.map_dns_profile(dp_ip,pol_dns_prof_name)

		else:
			policy_settings.append('N/A')
		###############################################





		with open(reports_path + 'dpconfig_map.csv', mode='a', newline="") as dpconfigmap_report:
			dp_configmap_writer = csv.writer(dpconfigmap_report, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			dp_configmap_writer.writerow(policy_settings)

		policy_settings.clear()





	def run(self):
		for dp_ip,dp_attr in self.full_pol_dic.items():
			dp_name = dp_attr['Name']
			dp_ver = dp_attr['Version']


			if self.isDPAvailable(dp_ip,dp_attr):

				for policy in dp_attr['Policies']['rsIDSNewRulesTable']: #key is rsIDSNewRulesTable, value is list of dictionary objects (each object is a dictionary which contains policy name and its attributes )
					pol_name = policy['rsIDSNewRulesName']
					# pol_bdos_prof_name = policy['rsIDSNewRulesProfileNetflood']
					if pol_name != 'null':
						self.map_policy(dp_name,dp_ver,dp_ip,pol_name,policy)

	


		report = reports_path + 'dpconfig_mapper.csv'
		logging_helper.logging.info('Config mapping is complete')
		print('Config mapping is complete')

		return report

