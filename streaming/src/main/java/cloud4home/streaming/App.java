package cloud4home.streaming;

import org.apache.log4j.Logger;

import cloud4home.streaming.config.ISinkAdapter;
import cloud4home.streaming.config.ISourceAdapter;
import cloud4home.streaming.config.PropertiesUtility;

import java.util.Properties;

/**
 * @author SimoneRomano
 *
 */
public class App {
	private static final Logger logger = Logger.getLogger(App.class.getName());

	/**
	 * 
	 */
	public App() {
		// TODO Auto-generated constructor stub
	}

	/**
	 * Google Cloud auth: 
	 * 	https://cloud.google.com/docs/authentication/production#obtaining_and_providing_service_account_credentials_manually
	 * @param args
	 * 	args[0] = properties file path
	 */
	public static void main(String[] args) {
		try {
			if (args.length < 1) {
				printUsage();
				System.exit(-1);
			}
			// logs a debug message
			logger.info("Starting Streaming manager...");

			// 1) readPropertiesFile
			logger.info("Reading properties file...");
			PropertiesUtility propReader = new PropertiesUtility(args[0]);
			Properties prop = propReader.getProperties();
			String sourceName = prop.getProperty("source.name");
			String sinkName = prop.getProperty("sink.name");
			
			Properties sourceProperties = propReader.getSubProperties("source." + sourceName + ".");
			Properties sinkProperties = propReader.getSubProperties("sink." + sinkName + ".");	
			
			logger.debug(sourceProperties.toString());	//sourceProperties.list(System.out);
			logger.debug(sinkProperties.toString());	//sinkProperties.list(System.out);
			
			
			// 2) Init Adapters
			logger.info("Init adapters...");
			
			//sink adpater init
			logger.info("Init sink adapters...");
			@SuppressWarnings("rawtypes")
			Class cSinkAdapter = Class.forName(sinkProperties.getProperty("class"));
			ISinkAdapter sink = (ISinkAdapter) cSinkAdapter.newInstance();
			sink.init(null, sinkProperties);
			
			//source adapter init
			logger.info("Init source adapters...");
			@SuppressWarnings("rawtypes")
			Class cSourceAdapter = Class.forName(sourceProperties.getProperty("class"));
			ISourceAdapter source = (ISourceAdapter) cSourceAdapter.newInstance();
			source.init(sink, sourceProperties);
						
			// 3) Start...
			logger.info("Streaming...");
			source.stream();
			
		} catch (Exception ex) {
			logger.error("Exception: " + ex.getMessage());
			ex.printStackTrace();
			System.exit(-1);
		}
		System.exit(0);
	}

	private static void printUsage() {
		String usage = "Usage: java -jar streaimng.jar config.properties";
		System.out.println(usage);		
	}

}