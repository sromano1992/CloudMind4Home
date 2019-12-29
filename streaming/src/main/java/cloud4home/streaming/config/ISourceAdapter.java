package cloud4home.streaming.config;

import java.io.IOException;
import java.util.Properties;

/**
 * 
 * @author SimoneRomano
 * Interface for source adapter
 */
public interface ISourceAdapter {
	public void init();
	public void init(ISinkAdapter sink, Properties prop) throws Exception;
	public void setProperties(Properties properties);
	public void stream();
}
