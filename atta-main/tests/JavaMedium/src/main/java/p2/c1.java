package p2;

import java.io.IOException;
import p1.*;

public class c1 {
	public c1() {
		System.out.println("  in p2.c1 creating p1.c1");
    p1.c1 p1c1 = new p1.c1();
		System.out.println("  in p2.c1 invoking p1.c1.run()");
    p1c1.run();
	}
	
	public void run() {
		System.out.println("  in p2.c1.run");
	}
}
