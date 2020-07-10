//    Copyright (C) 2020  Juan Pablo Orradre
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class SendmailUnix {

    private static final String SENDMAIL = "sendmail -R hdrs -N never -t -v <<< ";

	private static final String SHELL = "/bin/bash";

	private static final String SHELLPARAMS = "-c";

    private static String mailcont;

    public SendmailUnix(String from, String to, String subject, String message) {
		this.mailcont = "\"From: "+from+"\n"+
		"To: "+to+"\n"+
		"Subject: "+subject+"\n"+
		message+"\n"+
		".\"";
    }


	public static void main(String[] args){
		if (args.length<4){
			System.out.println("Arguments not set!! Usage: java SendmailUnix from to subject message");
		}else{
			SendmailUnix su = new SendmailUnix(args[0],args[1],args[2],args[3]);
			su.sendMail();
		}
	}

    public void sendMail() {
        String command = SENDMAIL + mailcont;
        try {
            Runtime r = Runtime.getRuntime();
            System.out.println("#### Command ####\n"+command+"\n");
            Process p = r.exec(new String[]{SHELL,SHELLPARAMS, command});
            p.waitFor();
			System.out.println ("Error code: \n" + p.exitValue());

			if (p.exitValue() == 0){
				
				BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));

				System.out.println("#### Command standard output ####\n");
				String s = null;
				while ((s = stdInput.readLine()) != null) {
					System.out.println(s);
				}

			}else{

				BufferedReader stdError = new BufferedReader(new InputStreamReader(p.getErrorStream()));

				System.out.println("#### Command standard error ####\n");
				String s = null;
				while ((s = stdError.readLine()) != null) {
					System.out.println(s);
				}
			}

        } catch (InterruptedException ex) {
            System.out.println(ex.getMessage());
        } catch (IOException ex) {
			System.out.println(ex.getMessage());
        }

    }
}
