import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.SocketException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLConnection;
import javax.xml.bind.DatatypeConverter;

import org.apache.commons.net.PrintCommandListener;
import org.apache.commons.net.ftp.FTP;
import org.apache.commons.net.ftp.FTPClient;
import org.apache.commons.net.ftp.FTPFile;
import org.apache.commons.net.ftp.FTPReply;

public class RequestHandlerFromFtp extends RequestHandlerHTTP10 {

	public RequestHandlerFromFtp(Socket socket) {
		super(socket);
	}

	protected void handleGet(HTTPRequest request, HTTPResponse response) throws IOException {
		long startTime = System.currentTimeMillis();
		FtpviaHttp.log(DateUtils.now() + ": NEW REQUEST");

		URI uri;
		try {
			uri = new URI(request.getURI());
		} catch (URISyntaxException e) {
			response.setStatusCode(400); // 400 is Bad Request
			handleException(request, response, "URISyntaxException", e);
			return;
		}

		String auth = request.headers.get("Authorization").substring(6); // cut off: Basic
		byte[] decodedBytes = DatatypeConverter.parseBase64Binary(auth);
		String authDecoded = new String();
		for (int i = 0; i < decodedBytes.length; ++i)
			authDecoded += String.valueOf((char) decodedBytes[i]);
		String[] userNameAndPassword = authDecoded.split(":");

		String fileName = uri.getRawPath();
		String[] fileNameAndServer = fileName.split("@");
		fileName = fileNameAndServer[0];

		String contentType = URLConnection.getFileNameMap().getContentTypeFor(fileName);
		response.setContentType(contentType);

		long fileSize = 0;

		String[] ftpHostAndPort = fileNameAndServer[1].split(":");
		String ftpHost = ftpHostAndPort[0];
		int ftpPort = Integer.parseInt(ftpHostAndPort[1]);

		final FTPClient ftp = new FTPClient();
		try {
	        // Detailed log (without login details)
	        ftp.addProtocolCommandListener(new PrintCommandListener(new PrintWriter(FtpviaHttp.logStream()), true));

	        // After connection attempt, you should check the reply code to verify success
			ftp.connect(ftpHost, ftpPort);
			if (!FTPReply.isPositiveCompletion(ftp.getReplyCode())) {
				throw new Exception("FTP server refused connection.");
			}

			// Login
			if (!ftp.login(userNameAndPassword[0], userNameAndPassword[1])) {
				ftp.logout();
				throw new Exception("FTP server refused login data.");
			}

			// Configure connection
			ftp.setFileType(FTP.BINARY_FILE_TYPE);
			ftp.enterLocalPassiveMode();

			// Get file size
			FTPFile[] f = ftp.listFiles(fileName);
			if (f.length > 0) {
				fileSize = f[0].getSize();
				response.setHeader(HTTPResponse.Header.ContentLength, Long.toString(fileSize));
			}

			response.flush();

			OutputStream out = response.getOutputStream();
			ftp.retrieveFile(fileName, out);
			out.close();
			
		} catch (IOException e) {
			if (ftp.isConnected())
				response.setStatusCode(ftp.getReplyCode());
			else
				response.setStatusCode(500);
			handleException(request, response, "IOException", e);
			
		} catch (Exception e) {
			response.setStatusCode(500);
			handleException(request, response, "Exception", e);
			
		} finally {
			if (ftp.isConnected()) {
				try {
					ftp.disconnect();
				} catch (IOException f) {
					// do nothing
				}
			}
		}

		long time = System.currentTimeMillis() - startTime;
		FtpviaHttp.log("226 Time " + time + " ms");
		if(fileSize > 0) {
			long bytesPerSecond = fileSize / time * 1000;
			FtpviaHttp.log("226 Transfer speed " + bytesPerSecond + " bps");
		}
	}

	protected void handle(HTTPRequest request, HTTPResponse response) throws IOException {
		try {
			if (!HTTPRequest.Method.GET.toString().equals(request.getMethod())) {
				response.setStatusCode(501); // 501 is "Not Implemented"
				return;
			} else
				handleGet(request, response);

		} catch (Exception ex) {
			handleException(request, response, "Server Error (Unexpected '"	+ ex.getMessage() + "' while handling request)", ex);
		}
	}

	private void handleException(HTTPRequest request, HTTPResponse response, String message, Exception ex) throws IOException {
		if (ex != null)
			FtpviaHttp.log(ex.getMessage());
		else
			FtpviaHttp.log(message);
		try {
			// If earlier code has already set a more precise HTTP error then leave that, 
			// make it a generic 500 only if its still the default 200
			if (response.getStatusCode() == 200) {
				response.setStatusCode(500);
			}

			PrintWriter pw = response.getPrintWriter();
			response.setContentType("text/html");

			pw.println("<html><head><title>Server Error</title></head><body><h1>Server Error</h1><p>");
			pw.println(message);
			pw.println("</p><pre>");
			if (ex != null) {
				ex.printStackTrace(pw);
			}
			pw.println("</pre></body></html>");
			
		} catch (IllegalStateException e) {
			// Oh, too late to getPrintWriter()? Well... log it but otherwise
			// ignore it; at least the setStatusCode() worked if we're here.
			FtpviaHttp.log(e.getMessage());
			return;
		}
	}
}
