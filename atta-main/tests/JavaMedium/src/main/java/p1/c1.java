package p1;

import java.io.IOException;
import lp1.*;

public class c1 {
	public c1() {
		System.out.println("  in p1.c1");
	}
	
	public void run() {
		System.out.println("  in p1.c1.run() creating lp1.c1");
    lp1.c1 lp1c1 = new lp1.c1();
    System.out.println("  in p1.c1.run() invoking lp1.c1.run()");
    lp1c1.run();
	}
}
