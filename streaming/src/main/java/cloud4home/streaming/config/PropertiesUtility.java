package cloud4home.streaming.config;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Map.Entry;
import java.util.Properties;

public class PropertiesUtility {
	private String filePath;
	private Properties prop;

	public PropertiesUtility(String filePath) throws FileNotFoundException, IOException {
		this.filePath = filePath;
		this.prop = new Properties();
		this.prop.load(new FileInputStream(this.filePath));
	}
	
	/**
	 * example: 
	 *  source.name=pubsubadapter
		source.pubsubadapter.type=cloud4home.streaming.source.gcloud.PubSub
		source.pubsubadapter.projectid=cloudmind4home
		source.pubsubadapter.topic=homeprobe
		source.pubsubadapter.subscriptionid=javastreaming
		
		input - initWith: source.pubsubadapter
		otput:
			type=cloud4home.streaming.source.gcloud.PubSub
			projectid=cloudmind4home
			topic=homeprobe
			subscriptionid=javastreaming
	 * @param initWith
	 * @return
	 */
	public Properties getSubProperties(String initWith) {
		Properties toReturn = null;
		if (this.prop == null) {
			return null;
		}
		
		toReturn = new Properties();
		if (initWith.equals("")) 
			return this.prop;
		for (Entry<Object, Object> entry : this.prop.entrySet()) {
			String key = entry.getKey().toString();
			if (key.startsWith(initWith)) {
				String toPut = key.substring(initWith.length());
				toReturn.put(toPut, entry.getValue());
			}
		}
		
		return toReturn;		
	}
	
	public Properties getProperties() {
		return this.prop;
	}
}
