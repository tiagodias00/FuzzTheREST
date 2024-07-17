

package com.example.application.services;

import io.github.cdimascio.dotenv.Dotenv;
import org.apache.commons.net.ftp.FTPClient;

import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

public class FtpService {

        public String uploadFileToFtp(String fileName, InputStream fileData) {
            FTPClient ftpClient = new FTPClient();
            try {
                Dotenv dotenv = Dotenv.load();
                String ftpHost = dotenv.get("FTP_HOST");
                int ftpPort = Integer.parseInt(dotenv.get("FTP_PORT"));
                String ftpUser = dotenv.get("FTP_USER");
                String ftpPassword = dotenv.get("FTP_PASSWORD");


                ftpClient.connect(ftpHost, ftpPort);


                ftpClient.login(ftpUser, ftpPassword);


                ftpClient.enterLocalPassiveMode();


                boolean success = ftpClient.storeFile(fileName, fileData);
                if (success) {

                    return ftpClient.printWorkingDirectory() + "/" + fileName;
                } else {
                    return null;
                }
            } catch (NumberFormatException e) {
                System.err.println("Invalid port format or other number format error: " + e.getMessage());
            } catch (IOException e) {
                System.err.println("FTP IO error: " + e.getMessage());
            } catch (Exception e) {
                System.err.println("General error: " + e.getMessage());
            } finally {
                if (ftpClient.isConnected()) {
                    try {
                        ftpClient.logout();
                        ftpClient.disconnect();
                        System.out.println("Disconnected from FTP server");
                    } catch (IOException e) {
                        System.err.println("Error disconnecting from FTP server: " + e.getMessage());
                    }
                }
            }
        return null;
        }
    }




