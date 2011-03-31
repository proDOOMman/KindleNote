//This is a *modifed* part of physkeybru hack for Kindle
//Logging disabled, and code influence only on this Kindlet

package main;

//import java.io.BufferedWriter;
//import java.io.FileWriter;
//import java.io.IOException;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import main.MyDispatcher;

public class Controller {
	MyDispatcher dsp;
//	BufferedWriter writer;
	public Controller(String kbdDir) {
		File mbkbd1 = new File(kbdDir,"keyboard.txt");
		File mbkbd2 = new File(kbdDir,"keyboard.txt");
		if(!mbkbd1.exists() && !mbkbd2.exists())
		{
			try {
				mbkbd1.createNewFile();
				FileWriter outFile = new FileWriter(mbkbd1);
				PrintWriter out = new PrintWriter(outFile);
				//яшерту раскладка - по дефолту
				out.print("q=я\n" +
				"w=ш\n" +
				"e=е\n" +
				"r=р\n" +
				"t=т\n" +
				"y=у\n" +
				"u=и\n" +
				"i=ь\n" +
				"o=о\n" +
				"p=п\n" +
				"a=а\n" +
				"s=с\n" +
				"d=д\n" +
				"f=ф\n" +
				"g=г\n" +
				"h=ы\n" +
				"j=ж\n" +
				"k=к\n" +
				"l=л\n" +
				"z=з\n" +
				"x=х\n" +
				"c=ц\n" +
				"v=в\n" +
				"b=б\n" +
				"n=н\n" +
				"m=м\n" +
				"Q=Я\n" +
				"W=Ш\n" +
				"E=Е\n" +
				"R=Р\n" +
				"T=Т\n" +
				"Y=У\n" +
				"U=И\n" +
				"I=Ч\n" +
				"O=О\n" +
				"P=П\n" +
				"A=А\n" +
				"S=С\n" +
				"D=Д\n" +
				"F=Ф\n" +
				"G=Г\n" +
				"H=Ы\n" +
				"J=Ж\n" +
				"K=К\n" +
				"L=Л\n" +
				"Z=З\n" +
				"X=Х\n" +
				"C=Ц\n" +
				"V=В\n" +
				"B=Б\n" +
				"N=Н\n" +
				"M=М\n" +
				"1=э\n" +
				"2=щ\n" +
				"3=ё\n" +
				"4=ч\n" +
				"5=,\n" +
				"6=ю\n" +
				"7=й\n" +
				"8=ъ\n" +
				"9=Щ\n" +
				"0=Э");
				out.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		/*
		try
		{
			this.writer = new BufferedWriter(new FileWriter("/mnt/us/developer/KindleNote/work/keyboard.log"));
		}
		catch (IOException localIOException)
		{
		}
		*/
		dsp = new MyDispatcher(this, kbdDir);
		MyLog("Kindlet loaded. Maybe");
	}
	void MyLog(String paramString)
	{
		/*
		try
		{
			this.writer.write(paramString + "\n");
			this.writer.flush();
		}
		catch (IOException localIOException)
		{
		}
		*/
	}
};