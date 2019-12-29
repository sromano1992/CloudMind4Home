package cloud4home.streaming.config;

import java.util.Properties;

/**
 * 
 * @author SimoneRomano
 * Interface for sink adapter
 */
public interface ISinkAdapter {
	public void init();
	public void init(ISourceAdapter source, Properties prop);
	public void setProperties(Properties properties) throws Exception;
	public void put(Object record) throws Exception;
}
