import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import p1.*;
import p2.*;
import b1.*;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;

class Args {
  @Parameter(names = "-r", description = "Run test")
  boolean version = false;
}

public class main {
  private static JCommander jc = null;

  static Properties config = new Properties();

  public static void loadConfig() {
    InputStream in = ClassLoader.getSystemResourceAsStream("v.i");
    try {
      config.load(in);
    }
    catch (Exception e) {
      config.setProperty("version", "(not known)");
    }
  }

  public static void main(String[] args) throws Exception {
    Args parsedArgs = new Args();
    try {
      jc = new JCommander(parsedArgs, args);
    }
    catch (Exception e) {
      System.err.println("ERROR: " + e.getMessage());
      return;
    }
    if (args.length == 0) {
      loadConfig();
      System.out.println("JavaMedium " + version.name + " (" + version.build + ")");
      jc.setProgramName("JavaMedium");
      jc.usage();
      return;
    }

    System.out.println("in main creating p1.c1");
    p1.c1 p1c1 = new p1.c1();
		System.out.println("in main creating p2.c1");
    p2.c1 p2c1 = new p2.c1();
		System.out.println("in main invoking p2.c1.run()");
    p2c1.run();

    b1.c1 b1c1 = new b1.c1();
    b1c1.run();
	}
}
