import java.io.IOException;
import p1.*;
import p2.*;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;

public class main {
  public static void main(String[] args) throws Exception {
		System.out.println("in main creating p1.c1");
    p1.c1 p1c1 = new p1.c1();
		System.out.println("in main creating p2.c1");
    p2.c1 p2c1 = new p2.c1();
		System.out.println("in main invoking p2.c1.run()");
    p2c1.run();
	}
}
