import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * A Server with a single "Worker thread" - serves one client after the next.  
 * @author vorburger
 */
public class ServerSingleThreadedWorker implements Runnable {

	private boolean runningServer;
	private IOException lastError;

	private final int port;
	private final int timeout;
	ServerSocket socketServer;
	
	RequestHandlerFactory requestHandlerFactory;
		
	/**
	 * Constructor
	 * @param port TCP/IP port number that the server will listen on
	 * @param timeout Timeout in miliseconds that the server will wait for a client to send the full request
	 * @param requestHandlerClass the RequestHandlerFactory that can provide a RequestHandler who will actually deal with network request 
	 */
	// TODO Alternative constructors, particularly with InetAddress bindingAddress (maybe backlog?)
	public ServerSingleThreadedWorker(int port, int timeout, RequestHandlerFactory requestHandlerFactory) {
		runningServer = false;
		this.port = port;
		this.timeout = timeout;
		this.requestHandlerFactory = requestHandlerFactory; 
	}

	/**
	 * Run the server.
	 * This is a blocking call - run() will not return, unless another thread sets runServer = false.
	 * @see ServerService
	 */
	// TODO Look into NIO - provide an alternative implementation?
	public void run() {
		if ( socketServer == null )
			throw new IllegalStateException("Call init() before run()  [Or consider using new ServerService]");

		try {
			// DO NOT set runningServer=true here - that's the responsability of start()
			
			while (runningServer) {
				Socket socket = socketServer.accept();
				if ( !runningServer )
					break;

				// Set timeout so that clients that are much too slow and would block the server for other clients can get their butt kicked
				// NOTE: This is a setSoTimeout() on the SOCKET, not on the SocketServer (@see unblockWaitingSocket)
				socket.setSoTimeout(timeout);
				
				RequestHandler handler = requestHandlerFactory.newRequestHandler(socket);
				this.handle(handler);
			}
		}
		// Note: An IOException from ServerSocket.accept() is NOT a recoverable condition (i.e. just log it and keep waiting for the next won't help)
		// Its occurence indicates e.g. a configuration problem that would justify aborting completly, i.e. stopping the server.
		// This is different from an Exception (IOException or other) occuring during the handling of one specific request above.
		catch (IOException ex) {
			runningServer = false;
			lastError = ex;
			
			FtpviaHttp.log(ex.getMessage());
			
			// This throw is probably not going anywhere anyway - there can be no catch for this...
			throw new RuntimeException("Unexpected problem during Socket binding/listening", ex);
		}
	}

	public IOException getLastError() {
		return lastError;
	}
	
	/**
	 * Serve the request from socket.
	 * Subclasses can override this method.
	 * 
	 * @param socket
	 * @throws IOException
	 * @throws SimpleWebServerException
	 */
	protected void handle(RequestHandler handler) {
		handler.run();
	}

	/**
	 * Set up - call this before run().
	 * @throws IOException
	 */
	public void init() throws IOException {
		this.start();
	}
	
	/**
	 * Start the server.
	 * This is a non-blocking protected internal method.
	 * @throws IOException Startup failed (often a BindException)
	 * @see ServerService#start()
	 */
	protected void start() throws IOException {
		if (runningServer)
			throw new IllegalStateException("Server is already running!");
		
		socketServer = new ServerSocket(port);
		runningServer = true;
	}

	/**
	 * Stop this server
	 * This is a non-blocking protected internal method.
	 * @see ServerService#stop()
	 */
	protected void stop() {
		if ( runningServer ) {
			runningServer = false;
			this.unblockWaitingSocket();

			try {
				socketServer.close();
			} catch (IOException ex) {
				// close() failed?  Boh, who cares, probably safe to ignore - caller could take any sensible action; we simply want it down anyway.
			}
		}
	}
	
	/**
	 * Private helper to "interrupt" the SocketServer.accept().
	 * This is needed because SocketServer.accept() is blocking, and we'd have to wait during shutdown until the next connection is accepted without this.
	 * @throws IOException 
	 */
	private void unblockWaitingSocket()  {
		// serverRunningTread.interrupt() or socketServer.close() don't seem to work here...
		// Alternative implementation could have been to use socketServer.setSoTimeout() above
		// so that SocketServer.accept() returns every say 1s or so and could break if runServer is false, but this "fake request" to unblock works too. 
		try {
			Socket socket = new Socket(InetAddress.getLocalHost(), port);
			PrintWriter pw = new PrintWriter( socket.getOutputStream() );
			pw.println("GET / HTTP/1.0");
			pw.flush();
			socket.close();
		}
		catch (IOException ex) {
			// This is only a problem is the server listener thread is still running
			// If it's not anymore, then the goal of this method was achieved though differently then intended (e.g. "real" incoming connection), we can silently ignore and return 
		}
	}
}
