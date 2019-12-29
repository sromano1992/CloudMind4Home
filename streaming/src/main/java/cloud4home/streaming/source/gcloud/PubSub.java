package cloud4home.streaming.source.gcloud;

import java.io.IOException;
import java.util.Properties;

import org.apache.log4j.Logger;

import com.google.cloud.pubsub.v1.AckReplyConsumer;
import com.google.cloud.pubsub.v1.MessageReceiver;
import com.google.cloud.pubsub.v1.Subscriber;
import com.google.cloud.pubsub.v1.SubscriptionAdminClient;
import com.google.common.util.concurrent.MoreExecutors;
import com.google.pubsub.v1.ProjectSubscriptionName;
import com.google.pubsub.v1.ProjectTopicName;
import com.google.pubsub.v1.PubsubMessage;
import com.google.pubsub.v1.PushConfig;
import cloud4home.streaming.config.ISinkAdapter;
import cloud4home.streaming.config.ISourceAdapter;

public class PubSub implements ISourceAdapter {
	private static final Logger logger = Logger.getLogger(PubSub.class.getName());
	private ISinkAdapter sink;
	private ProjectSubscriptionName subscription;

	@Override
	public void init() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void init(ISinkAdapter sink, Properties prop) throws Exception {
		this.sink = sink;

		logger.debug("ProjectId: " + prop.getProperty("projectid"));
		logger.debug("topic: " + prop.getProperty("topic"));

		this.subscription = ProjectSubscriptionName.of(prop.getProperty("projectid"),
				prop.getProperty("subscriptionid"));
	}

	@Override
	public void setProperties(Properties properties) {
		// TODO Auto-generated method stub

	}

	@Override
	public void stream() {

		Subscriber subscriber = null;
		try {
			StreamMessageReceiver receiver = new StreamMessageReceiver(this.sink);

			subscriber = Subscriber.newBuilder(subscription, receiver).build();
			subscriber.addListener(new Subscriber.Listener() {
				@Override
				public void failed(Subscriber.State from, Throwable failure) {
					logger.error(failure.getMessage() + " - " + failure.getStackTrace());
				}
			}, MoreExecutors.directExecutor());
			subscriber.startAsync().awaitTerminated();
		} finally {
			if (subscriber != null) {
				subscriber.stopAsync().awaitTerminated();
			}
		}
	}
}
