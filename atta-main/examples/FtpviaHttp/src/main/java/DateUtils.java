import java.text.SimpleDateFormat;
import java.util.Calendar;

public class DateUtils {
	public static String nowWithFormat(String format) {
		Calendar cal = Calendar.getInstance();
		SimpleDateFormat sdf = new SimpleDateFormat(format);
		return sdf.format(cal.getTime());
	}

	public static final String DATE_FORMAT_NOW = "yyyy-MM-dd HH:mm:ss";

	public static String now() {
		return nowWithFormat(DATE_FORMAT_NOW);
	}

	public static final String DATE_FORMAT_NOW_AS_FILE_NAME = "yyyy-MM-dd HH:mm:ss";

	public static String nowAsFileName() {
		return nowWithFormat(DATE_FORMAT_NOW_AS_FILE_NAME);
	}
}