package cloud4home.streaming.sink.gcloud;

import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.log4j.Logger;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.util.Properties;

import cloud4home.streaming.App;
import cloud4home.streaming.config.ISinkAdapter;
import cloud4home.streaming.config.ISourceAdapter;

import com.google.api.client.util.DateTime;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryError;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.InsertAllRequest;
import com.google.cloud.bigquery.InsertAllResponse;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import java.util.UUID;

public class BigQuerySink implements ISinkAdapter {
	private static final Logger logger = Logger.getLogger(BigQuerySink.class.getName());
	private TableId tableId;
	private BigQuery bigquery;
	private Properties prop;

	@Override
	public void init() {
		// TODO Auto-generated method stub

	}

	@Override
	public void init(ISourceAdapter source, Properties prop) {
		this.prop = prop;
		this.bigquery = BigQueryOptions.getDefaultInstance().getService();
		this.tableId = TableId.of(prop.getProperty("dataset"), prop.getProperty("table"));
	}

	@Override
	public void setProperties(Properties properties) throws Exception {
		// TODO Auto-generated method stub
		throw new Exception("Not implemented yet!");
	}

	@Override
	//more details: 
	//	https://cloud.google.com/bigquery/streaming-data-into-bigquery#bigquery_table_insert_rows-java
	public void put(Object record) throws Exception {
		JSONParser parser = new JSONParser();
		JSONObject json = (JSONObject) parser.parse(record.toString());
		
		Map<String, Object> rowContent = new HashMap<>();
		if (json.containsKey("offChipTempValue"))	rowContent.put("offChipTempValue", json.get("offChipTempValue"));
		if (json.containsKey("offChipTempStatus"))	rowContent.put("offChipTempStatus", json.get("offChipTempStatus"));
		if (json.containsKey("offChipTempMessage"))	rowContent.put("offChipTempMessage", json.get("offChipTempMessage"));
		if (json.containsKey("onboardBrightnessValue"))	rowContent.put("onboardBrightnessValue", json.get("onboardBrightnessValue"));
		if (json.containsKey("onboardBrightnessStatus"))	rowContent.put("onboardBrightnessStatus", json.get("onboardBrightnessStatus"));
		if (json.containsKey("onboardBrightnessMessage"))	rowContent.put("onboardBrightnessMessage", json.get("onboardBrightnessMessage"));
		if (json.containsKey("onboardTemperatureValue"))	rowContent.put("onboardTemperatureValue", json.get("onboardTemperatureValue"));
		if (json.containsKey("onboardTemperatureStatus"))	rowContent.put("onboardTemperatureStatus", json.get("onboardTemperatureStatus"));
		if (json.containsKey("onboardHumidityValue"))	rowContent.put("onboardHumidityValue", json.get("onboardHumidityValue"));
		if (json.containsKey("onboardHumidityStatus"))	rowContent.put("onboardHumidityStatus", json.get("onboardHumidityStatus"));
		if (json.containsKey("onboardTemperatureMessage"))	rowContent.put("onboardTemperatureMessage", json.get("onboardTemperatureMessage"));
		if (json.containsKey("onboardHumidityMessage"))	rowContent.put("onboardHumidityMessage", json.get("onboardHumidityMessage"));
		if (json.containsKey("barometerTemperaturValue"))	rowContent.put("barometerTemperaturValue", json.get("barometerTemperaturValue"));
		if (json.containsKey("barometerTemperaturStatus"))	rowContent.put("barometerTemperaturStatus", json.get("barometerTemperaturStatus"));
		if (json.containsKey("barometerPressureValue"))	rowContent.put("barometerPressureValue", json.get("barometerPressureValue"));
		if (json.containsKey("barometerPressureStatus"))	rowContent.put("barometerPressureStatus", json.get("barometerPressureStatus"));
		if (json.containsKey("barometerTemperatureMessage"))	rowContent.put("barometerTemperatureMessage", json.get("barometerTemperatureMessage"));
		if (json.containsKey("barometerPressureMessage"))	rowContent.put("barometerPressureMessage", json.get("barometerPressureMessage"));
		if (json.containsKey("presenceValue"))	rowContent.put("presenceValue", json.get("presenceValue"));
		if (json.containsKey("presenceStatus"))	rowContent.put("presenceStatus", json.get("presenceStatus"));
		if (json.containsKey("presenceMessage"))	rowContent.put("presenceMessage", json.get("presenceMessage"));
		if (json.containsKey("rilevationTime")) {
			SimpleDateFormat dateFormat = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss.SSSSSS");  
		    Date d1 = dateFormat.parse((String)json.get("rilevationTime"));
		    SimpleDateFormat dateFormatTarget = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSSSS");
		    String stringDateTarget = dateFormatTarget.format(d1);
			rowContent.put("rilevationTime", stringDateTarget);
			//rowContent.put("rilevationTime", "2019-06-11T14:44:31");
		}
		if (json.containsKey("imei"))	rowContent.put("imei", json.get("imei"));
		if (json.containsKey("props"))	rowContent.put("props", json.get("props").toString());
		
		Instant t1 = Instant.now();
		InsertAllResponse response = bigquery.insertAll(InsertAllRequest.newBuilder(tableId).addRow(rowContent)
				// More rows can be added in the same RPC by invoking .addRow() on the builder.
				// You can also supply optional unique row keys to support de-duplication
				// scenarios.
				.build());
		Instant t2 = Instant.now();
		long ns = Duration.between(t1, t2).toMillis();
		logger.info("Duration: " + ns + " ms");
		
		if (response.hasErrors()) {
			for (Entry<Long, List<BigQueryError>> entry : response.getInsertErrors().entrySet()) {
				logger.error(entry.toString());
			}
		}
	}

	public static void main(String[] args) {
		
	}

}
