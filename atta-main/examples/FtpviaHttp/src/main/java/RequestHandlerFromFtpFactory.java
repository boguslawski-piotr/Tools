import java.net.Socket;


public class RequestHandlerFromFtpFactory implements RequestHandlerFactory {

	@Override
	public RequestHandler newRequestHandler(Socket socket) {
		return new RequestHandlerFromFtp(socket);
	}

}
