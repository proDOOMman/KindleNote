/*

    Copyright (c) 2011 by Stanislav (proDOOMman) Kosolapov <prodoomman@gmail.com>

 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************
*/

package main;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.Insets;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;

import com.amazon.kindle.kindlet.event.KindleKeyCodes;
import com.amazon.kindle.kindlet.ui.KLabel;

public class KFakeMenuItem extends KLabel {
	/**
	 * Menu item
	 */
	private String m_text;
	private static final long serialVersionUID = 8165263848502840240L;
	private int maxLen = 30;

	public void init()
	{
		this.setMinimumSize(new Dimension(600,20));// ???
		this.setMargin(new Insets(10,10,10,10));
		this.setFont(new Font(getFont().getName(),Font.PLAIN,28));
		this.setFocusable(true);
		this.addFocusListener(new FocusListener() {
			public void focusLost(FocusEvent arg0) {
				if(m_text.length()>maxLen)
					setText(m_text.substring(0, maxLen-3)+"...");
				else
					setText(m_text);
				setFont(new Font(getFont().getName(),Font.PLAIN,28));
				Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
						new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "F0"));
			}
			public void focusGained(FocusEvent arg0) {
				setFont(new Font(getFont().getName(),Font.BOLD,28));
				if(m_text.length()>maxLen-2)
					setText("-> "+m_text.substring(0, maxLen-5)+"...");
				else
					setText("-> "+m_text);

				Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
						new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "F1"));
			}
		});
		this.addKeyListener(new KeyListener() {
			public void keyTyped(KeyEvent e) {}
			public void keyReleased(KeyEvent e) {
				if(e.getKeyCode() == KindleKeyCodes.VK_FIVE_WAY_SELECT ||
						KeyEvent.getKeyText(e.getKeyCode())=="Enter")
				{
					//edit
					Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
							new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "E"+m_text));
				}
				else if (KeyEvent.getKeyText(e.getKeyCode())=="Backspace")
				{
					//delete
					Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
							new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "D"+m_text));
				}
				else if (e.getKeyChar()=='e'||e.getKeyChar()=='E')
				{
					Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
							new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "W"+m_text));
				}
				else if (e.getKeyChar()=='r'||e.getKeyChar()=='R')
				{
					Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
							new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "R"+m_text));
				}
				else if (e.getKeyChar()=='n'||e.getKeyChar()=='N')
				{
					Toolkit.getDefaultToolkit().getSystemEventQueue(). postEvent(
							new ActionEvent(self(), ActionEvent.ACTION_PERFORMED, "N"));
				}
			}
			public void keyPressed(KeyEvent e) {}
		});
	}
	
	public KFakeMenuItem() {
		init();
	}
	
	public KFakeMenuItem(String text)
	{
		init();
		m_text = text;
		if(m_text.length()>maxLen)
			setText(m_text.substring(0, maxLen-2)+"...");
		else
			setText(m_text);
	}
	
	public KFakeMenuItem self(){
		return this;
	}
	
	public String getText()
	{
		return m_text;
	}
	
	public void setMText(String text)
	{
		m_text = text;
		if(this.hasFocus())
		{
			if(m_text.length()>maxLen-2)
				setText("-> "+m_text.substring(0, maxLen-5)+"...");
			else
				setText("-> "+m_text);
		}
		else
		{
			if(m_text.length()>maxLen)
				setText(m_text.substring(0, maxLen-2)+"...");
			else
				setText(m_text);
		}
	}
}
