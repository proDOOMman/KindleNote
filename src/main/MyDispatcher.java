// This is a part of physkeybru hack for Kindle

package main;

//import java.awt.EventQueue;
import java.awt.KeyEventDispatcher;
import java.awt.KeyboardFocusManager;
//import java.awt.Toolkit;
import java.awt.event.KeyEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.util.HashMap;

public class MyDispatcher
  implements KeyEventDispatcher
{
  private HashMap trans;
  private boolean keyboardEnabled;
  private boolean keyboardEN;
  private KeyboardFocusManager man;
  private KeyEvent ShiftEvent;
  private boolean ShiftConsumed;
  private boolean SimpleMode;
  private char prev_c;
//  private EventQueue eq;
  private Controller cont;

  public MyDispatcher(Controller paramController, String kbdDir)
  {
    this.cont = paramController;
    this.trans = new HashMap();
    this.keyboardEnabled = false;
    this.keyboardEN = true;
    this.ShiftConsumed = false;
    this.SimpleMode = false;
    this.prev_c = ' ';
//    EventQueue localEventQueue = Toolkit.getDefaultToolkit().getSystemEventQueue();
    this.man = KeyboardFocusManager.getCurrentKeyboardFocusManager();
    this.man.addKeyEventDispatcher(this);
    Object localObject;
    /*
    Field[] arrayOfField = KeyboardFocusManager.class.getDeclaredFields();
    for (int i = 0; i < arrayOfField.length; i++)
    {
      this.cont.MyLog(arrayOfField[i].getName() + " " + arrayOfField[i].getType().getName());
      if (!"keyEventDispatchers".equals(arrayOfField[i].getName()))
        continue;
      localObject = arrayOfField[i];
      ((Field)localObject).setAccessible(true);
      try
      {
        this.cont.MyLog("Getting dispatchers list");
        Object[] arrayOfObject1 = (Object[])(Object[])((Field)localObject).get(this.man);
        this.cont.MyLog("Insert our handler");
        for (int j = 0; j < arrayOfObject1.length; j++)
          this.cont.MyLog(arrayOfObject1[j].toString());
        Object[] arrayOfObject2 = new Object[arrayOfObject1.length + 1];
        System.arraycopy(arrayOfObject1, 0, arrayOfObject2, 1, arrayOfObject1.length);
        arrayOfObject2[0] = this;
        ((Field)localObject).set(this.man, arrayOfObject2);
        this.cont.MyLog("success");
      }
      catch (Exception localException)
      {
        this.cont.MyLog(localException.toString());
      }
    }
    */
    this.SimpleMode = new File(kbdDir+"/keyboard_european.txt").exists();
    File localFile;
    if (this.SimpleMode)
      localFile = new File(kbdDir+"/keyboard_european.txt");
    else
      localFile = new File(kbdDir+"/keyboard.txt");
    if (localFile.exists())
    {
      try
      {
        localObject = new FileInputStream(localFile);
      }
      catch (FileNotFoundException localFileNotFoundException)
      {
        this.cont.MyLog(localFileNotFoundException.getMessage());
        return;
      }
      BufferedReader localBufferedReader;
      try
      {
        localBufferedReader = new BufferedReader(new InputStreamReader((InputStream)localObject, "UTF-8"));
      }
      catch (UnsupportedEncodingException localUnsupportedEncodingException)
      {
        this.cont.MyLog(localUnsupportedEncodingException.getMessage());
        return;
      }
      this.cont.MyLog("Reading: " + localFile.getAbsolutePath());
      try
      {
        String str1;
        while ((str1 = localBufferedReader.readLine()) != null)
        {
          if (str1.indexOf("=") <= 0)
            continue;
          String str2 = str1.substring(0, str1.indexOf("="));
          String str3 = str1.substring(str1.indexOf("=") + 1, str1.length());
          this.trans.put(str2, str3);
          this.cont.MyLog(str2 + '=' + str3);
        }
      }
      catch (IOException localIOException)
      {
        this.cont.MyLog(localIOException.getMessage());
        return;
      }
      this.keyboardEnabled = true;
    }
    else
    {
      this.cont.MyLog("File not found: " + localFile.getAbsolutePath());
    }
  }

  public boolean dispatchKeyEvent(KeyEvent paramKeyEvent)
  {
    if (this.keyboardEnabled)
    {
      this.cont.MyLog(paramKeyEvent.toString());
      char c1 = paramKeyEvent.getKeyChar();
      String str;
      if (this.SimpleMode)
      {
        if (paramKeyEvent.getID() == 400)
        {
          str = String.valueOf(this.prev_c) + String.valueOf(c1);
          this.cont.MyLog("Check for: " + str);
          if (this.trans.containsKey(str))
          {
            paramKeyEvent.consume();
            char c2 = ((String)this.trans.get(str)).charAt(0);
            this.cont.MyLog("Translate to: " + c2);
            this.prev_c = ' ';
            this.man.dispatchEvent(new KeyEvent(paramKeyEvent.getComponent(), 401, System.currentTimeMillis(), 0, 8, (char) 65535));
            this.man.dispatchEvent(new KeyEvent(paramKeyEvent.getComponent(), 400, System.currentTimeMillis(), 0, 0, '\b'));
            this.man.dispatchEvent(new KeyEvent(paramKeyEvent.getComponent(), 402, System.currentTimeMillis(), 0, 8, (char) 65535));
            this.man.dispatchEvent(new KeyEvent(paramKeyEvent.getComponent(), 400, System.currentTimeMillis(), 0, 0, c2));
            return true;
          }
          this.prev_c = c1;
        }
        return false;
      }
      if ((paramKeyEvent.getKeyCode() == 16) && (paramKeyEvent.getID() == 401))
      {
        this.ShiftEvent = paramKeyEvent;
        this.ShiftConsumed = true;
        return true;
      }
      if ((c1 == ' ') && (paramKeyEvent.isShiftDown()))
      {
        paramKeyEvent.consume();
        if (paramKeyEvent.getID() == 401)
        {
          this.keyboardEN = (!this.keyboardEN);
          this.cont.MyLog("Keyboard switched: " + this.keyboardEN);
        }
        this.ShiftConsumed = false;
        return true;
      }
      if (this.ShiftConsumed)
      {
        this.man.dispatchEvent(this.ShiftEvent);
        this.cont.MyLog("Shift state redispatched");
      }
      if (!this.keyboardEN)
      {
        if (this.ShiftConsumed)
          c1 = Character.toUpperCase(c1);
        str = String.valueOf(c1);
        if (this.trans.containsKey(str))
        {
          paramKeyEvent.setKeyChar(((String)this.trans.get(str)).charAt(0));
          this.cont.MyLog("Translated to: " + paramKeyEvent.getKeyChar());
        }
      }
      else if (this.ShiftConsumed)
      {
        paramKeyEvent.setKeyChar(Character.toUpperCase(paramKeyEvent.getKeyChar()));
      }
      if ((this.ShiftConsumed) && (paramKeyEvent.getID() == 400))
        this.ShiftConsumed = false;
    }
    return false;
  }
}