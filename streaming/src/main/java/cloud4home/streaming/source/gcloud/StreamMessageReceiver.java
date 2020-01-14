package cloud4home.streaming.source.gcloud;

import org.apache.log4j.Logger;

import com.google.cloud.pubsub.v1.AckReplyConsumer;
import com.google.cloud.pubsub.v1.MessageReceiver;
import com.google.protobuf.ByteString;
import com.google.pubsub.v1.PubsubMessage;

import cloud4home.streaming.config.ISinkAdapter;

public class StreamMessageReceiver implements MessageReceiver {
	private static final Logger logger = Logger.getLogger(StreamMessageReceiver.class.getName());
	private ISinkAdapter sink;

	public StreamMessageReceiver(ISinkAdapter sink) {
		this.sink = sink;
	}

	@Override
	public void receiveMessage(PubsubMessage message, AckReplyConsumer consumer) {
		//this.sink.put(message.toString());
		logger.debug("New message! - " + message.toString());
		String data = message.getData().toStringUtf8();
		String record = data.substring(data.indexOf("{"), data.length());

		try {
			this.sink.put(record);
			consumer.ack();
		} catch (Exception e) {
			logger.error("Exception: " + e.getMessage(), e);
		}
	}

}
