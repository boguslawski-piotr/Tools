import java.io.IOException;

/**
 * Runs a Server in a separate thread.
 * @author vorburger
 */
public class ServerService {
	
	private ServerSingleThreadedWorker runnableServer;
	private Thread serverRunningTread;

	public ServerService(ServerSingleThreadedWorker runnableServer) {
		this.runnableServer = runnableServer; 
	}
	
	/**
	 * Start the server.
	 * This is a non-blocking call - it will fork a new thread and run() and then return.
	 * @throws IOException Startup failed (often a BindException)
	 */
	public void start() throws IOException {
		runnableServer.start();
		serverRunningTread = new Thread(runnableServer, "Server Listener Thread (listening for incoming network connections)");
		serverRunningTread.start();
	}
	
	public void stop() {
		runnableServer.stop();
		while ( serverRunningTread.isAlive() ) {
			// Wait for server listener thread to exit... just to be sure.
		}
	}
}
