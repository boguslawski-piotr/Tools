import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.PrintStream;
import java.util.Properties;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;

class Args {
  @Parameter(names = "-l", description = "Log file")
  String  logFile           = null;

  @Parameter(names = "-p", description = "HTTP port")
  int     port              = 80;

  @Parameter(names = "-m", description = "Max threads")
  int     maxThreads        = 10;

  @Parameter(names = "-t", description = "Client timeout (in ms)")
  int     clientTimeoutInMS = 1000;

  @Parameter(names = "-v", description = "Print program version")
  boolean version           = false;

  @Parameter(names = "-h", description = "Print usage")
  boolean help              = false;
}

public class FtpviaHttp {
  private static JCommander  jc         = null;
  private static Args        parsedArgs = new Args();
  private static PrintStream log        = null;

  public static PrintStream logStream() {
    return log;
  }

  public static void log(String msg) {
    if (parsedArgs.logFile == null)
      log = System.out;
    else {
      try {
        if (log == null)
          log = new PrintStream(parsedArgs.logFile);
      }
      catch (FileNotFoundException e) {}
    }

    try {
      if (log != null) {
        log.println(msg);
        log.flush();
      }
    }
    catch (Exception e) {}
  }

  public static void main(String[] args) throws Exception {
    loadConfig();

    try {
      jc = new JCommander(parsedArgs, args);
    }
    catch (Exception e) {
      System.err.println("ERROR: " + e.getMessage());
      return;
    }
    if (parsedArgs.help) {
      printHelp();
      return;
    }
    if (parsedArgs.version) {
      printVersion();
      return;
    }

    RequestHandlerFactory requestHandlerFactory = new RequestHandlerFromFtpFactory();
    ServerMultiThreadedWorkers server = new ServerMultiThreadedWorkers(parsedArgs.port, parsedArgs.clientTimeoutInMS,
                                                                       parsedArgs.maxThreads, requestHandlerFactory);
    server.init();

    log(DateUtils.now() + ": " + getProgramName() + " " + getVersion() + " ready (on HTTP port " + parsedArgs.port + ")");
    server.run();

    if (log != null)
      log.close();

    // Can Ctrl-C/kill signal - we assume that shutdowns the VM, so we are
    // not too concerned with proper close() here (in the TestCases we are)
  }

  static Properties config = new Properties();

  public static void loadConfig() {
    InputStream in = ClassLoader.getSystemResourceAsStream("version.number");
    try {
      config.load(in);
    }
    catch (Exception e) {
      config.setProperty("version", "(not known)");
    }
  }

  public static String getProgramName() {
    return "FtpviaHttp";
  }

  public static String getVersion() {
    return config.getProperty("version");
  }

  private static void printVersion() {
    System.out.println(getProgramName() + " v" + getVersion() + "\n");
  }

  private static void printHelp() {
    printVersion();
    jc.setProgramName(getProgramName());
    jc.usage();
  }

}
