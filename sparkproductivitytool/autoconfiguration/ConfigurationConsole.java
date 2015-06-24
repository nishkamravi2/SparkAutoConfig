import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.Enumeration;
import java.util.Hashtable;

import security.Security;
import sparkR.SparkR;
import sql.SQL;
import streaming.Streaming;
import core.standalone.*;
import core.yarn.CoreYarn;
import dynamicallocation.DynamicAllocation;

public class ConfigurationConsole {
	
	@SuppressWarnings("unused")
	public static void main(String[] args) {

		// input config parameters
		String inputDataSize = ""; // in GB
		String numNodes = "";
		String numCoresPerNode = "";
		String memoryPerNode = ""; // in GB
		String numJobs = "";
		String fileSystem = ""; // ext4, ext3, etc
		String master = ""; // standalone, yarn
		String deployMode = ""; // client, cluster
		String clusterManager = ""; // standalone, yarn
		String sqlFlag = ""; // y, n
		String streamingFlag = "";// y, n
		String dynamicAllocationFlag = "";//y, n
		String securityFlag = "";// y, n
		String sparkRFlag = "";// y, n
		String className = ""; // name of app class
		String appJar = ""; // app Jar URL
		String appArgs = ""; // app args as a single string
		
		//output tables
		Hashtable<String, String> optionsTable = new Hashtable<String, String>();
		Hashtable<String, String> recommendationsTable = new Hashtable<String, String>();
		Hashtable<String, String> commandLineParamsTable = new Hashtable<String, String>();
		
		String cmdLineParams = "";
		
		// get input parameters
		if (args.length != 17) {
			printUsage();
			System.exit(0);
		} else {
			inputDataSize = args[0];
			numNodes = args[1];
			numCoresPerNode = args[2];
			memoryPerNode = args[3];
			numJobs = args[4];
			fileSystem = args[5];
			master = args[6];
			deployMode = args[7];
			clusterManager = args[8];
			sqlFlag = args[9];
			streamingFlag = args[10];
			dynamicAllocationFlag = args[11];
			securityFlag = args[12];
			sparkRFlag = args[13];
			className = args[14];
			appJar = args[15];
			appArgs = args[16];
		}
		
		//first initalize standard/standalone parameters
		CoreStandalone.configureStandardSettings(args, optionsTable, recommendationsTable, commandLineParamsTable);
		
		//if it is yarn, add in the Yarn settings
		if (clusterManager.equals("yarn")){ CoreYarn.configureYarnSettings(args, optionsTable, recommendationsTable, commandLineParamsTable);}
		
		//configure necessary Dynamic Allocation settings
		if (dynamicAllocationFlag.equals("y")){ DynamicAllocation.configureDynamicAllocationSettings(args, optionsTable, recommendationsTable, commandLineParamsTable);}
		
		//configure necessary SQL settings
		if (sqlFlag.equals("y")){ SQL.configureSQLSettings(args, optionsTable, recommendationsTable, commandLineParamsTable); }
		
		//configure necessary Streaming settings
		if (streamingFlag.equals("y")){ Streaming.configureStreamingSettings(args, optionsTable, recommendationsTable, commandLineParamsTable);}
		
		//configure necessary Security settings
		if (securityFlag.equals("y")){ Security.configureSecuritySettings(args, optionsTable, recommendationsTable, commandLineParamsTable);}
		
		//configure necessary SparkR settings
		if (sparkRFlag.equals("y")){ SparkR.configureSparkRSettings(args, optionsTable, recommendationsTable, commandLineParamsTable);}

		try {
			//Creating the .conf file
			File conf_file = new File("spark.conf");
			if (!conf_file.exists()) {
				conf_file.createNewFile();
			}
			//Creating the recommendations file
			BufferedWriter b1 = new BufferedWriter(
					new FileWriter(conf_file));

			File advise_file = new File("spark.conf.advise");
			if (!advise_file.exists()) {
				advise_file.createNewFile();
			}
			
			//Creating the command line options file
			BufferedWriter b2 = new BufferedWriter(new FileWriter(
					advise_file));

			File cmd_options_file = new File("spark.cmdline.options");
			if (!cmd_options_file.exists()) {
				cmd_options_file.createNewFile();
			}
			BufferedWriter b3 = new BufferedWriter(new FileWriter(
					cmd_options_file));

			//Populating Options
			Enumeration<String> it = optionsTable.keys();
			while (it.hasMoreElements()) {
				String key = (String) it.nextElement();
				String value = (String) optionsTable.get(key);
				// if nothing was set, do not add it to .conf file
				if (value.equals("")) {
					continue;
				}
				b1.write(key + " 			" + value + "\n");
			}
			b1.close();

			//Populating Recommendations
			it = recommendationsTable.keys();
			while (it.hasMoreElements()) {
				String key = (String) it.nextElement();
				String value = (String) recommendationsTable.get(key);
				// if nothing was set, do not add it to .conf file
				if (value.equals("")) {
					continue;
				}
				b2.write(key + " 			" + value + "\n");
			}
			b2.close();

			//Populating Command Line Params
			it = commandLineParamsTable.keys();
			while (it.hasMoreElements()) {
				String key = (String) it.nextElement();
				String value = (String) commandLineParamsTable.get(key);
				b3.write(key + " 			" + value + "\n");
				cmdLineParams += " " + key + " " + value;
			}
			b3.close();
		} catch (Exception e) {
			e.printStackTrace();
		}

		constructCmdLine(args, optionsTable, recommendationsTable, commandLineParamsTable, cmdLineParams);
	}
	public static void printUsage() {
		System.out.println("\nUsage: \n"
				+ "java SparkConfigure "
				+ "<input data size in GB> "
				+ "<number of nodes in cluster> "
				+ "<number of cores per node> "
				+ "<memory per node in GB> "
				+ "<number of jobs> "
				+ "<filesystem type> "
				+ "<master: standalone URL/yarn> "
				+ "<deployMode: cluster/client> "
				+ "<clusterManger: standalone/yarn> "
				+ "<sql: y/n> "
				+ "<streaming: y/n> "
				+ "<dynamicAllocation: y/n> "
				+ "<security: y/n> "
				+ "<sparkR: y/n> "
				+ "<app className> "
				+ "<app JAR location> "
				+ "<app arguments as one string>\n");
	}

	public static void constructCmdLine(String[] args, Hashtable<String, String> optionsTable, Hashtable<String, String> recommendationsTable, Hashtable<String, String> commandLineParamsTable, String cmdLineParams){
		String master = args[6];
		String deployMode = args[7];
		String className = args[14];
		String appJar = args[15];
		String appArgs = args[16];
		String driverMemory = optionsTable.get("spark.driver.memory");
		String driverExtraClassPath = optionsTable.get("spark.driver.extraClassPath");
		String driverExtraJavaOptions = optionsTable.get("spark.driver.extraJavaOptions");
		String driverExtraLibraryPath = optionsTable.get("spark.driver.extraLibraryPath");
		String cmdLine = "Invalid --deploy-mode argument";
		if (deployMode.equals("client")){
			//Some arguments needs to be run at command line in client mode
			String clientModeOnlyArguments = "";
			if (driverExtraClassPath.length() > 0){
				clientModeOnlyArguments += " --driver-class-path " + driverExtraClassPath;
			}
			if (driverExtraJavaOptions.length() > 0){
				clientModeOnlyArguments += " --driver-java-options " + driverExtraJavaOptions;
			}
			if (driverExtraLibraryPath.length() > 0){
				clientModeOnlyArguments += " --driver-library-path " + driverExtraLibraryPath;
			}
			System.out.println(clientModeOnlyArguments);
			cmdLine = "spark-submit --master " + master + " --deploy-mode " + deployMode + " --driver-memory " + driverMemory + clientModeOnlyArguments + " --class " + className + " --properties-file spark.conf " + cmdLineParams + " " + 
					appJar + " " + appArgs;
		}
		else if (deployMode.equals("cluster")){
			cmdLine = "spark-submit --master " + master + " --deploy-mode " + deployMode + " --driver-memory " + driverMemory + " --class " + className + " --properties-file spark.conf " + cmdLineParams + " " + 
					appJar + " " + appArgs;
		}else{
			cmdLine = "Invalid Argument for deployMode";
		}
		System.out.println("\nAuto-generated files: spark.conf, spark.conf.advise and spark.cmdline.options\n");
		System.out.println("Invoke command line: " + cmdLine + "\n");
	}
}
