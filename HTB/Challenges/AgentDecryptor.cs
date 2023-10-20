using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
using System.Collections.Generic;

class AgentDecryptor {
  
    static void Main()
    {
        string directloc = Directory.GetCurrentDirectory();
        var fyles = Directory.EnumerateFiles(directloc, "*", SearchOption.AllDirectories);
        Console.WriteLine("Current folder and files: ");
        Console.WriteLine(String.Join(Environment.NewLine, fyles));

        foreach (var file in fyles)
        {
                IEnumerable<string> lines = File.ReadLines(file);
                foreach (var line in lines)
                {
                        Console.WriteLine(Decrypt(line));
                        //Console.WriteLine(Encoding.UTF8.GetString(line));
                }
        }
    
    }
    
    private static string Decrypt(string pt)
    {
        Console.WriteLine(pt);
        string key = "AKaPdSgV";
        string iv = "QeThWmYq";
        byte[] keyBytes = Encoding.UTF8.GetBytes(key);
        byte[] ivBytes = Encoding.UTF8.GetBytes(iv);
        byte[] inputBytes = Convert.FromBase64String(pt);
        
        using (DESCryptoServiceProvider dsp = new DESCryptoServiceProvider())
        {
            var mstr = new MemoryStream();
            var crystr = new CryptoStream(mstr, dsp.CreateDecryptor(keyBytes, ivBytes), CryptoStreamMode.Write);
            crystr.Write(inputBytes, 0, inputBytes.Length);
            crystr.FlushFinalBlock();
            byte[] decrpt = new byte[mstr.Length];
            mstr.Position = 0;
            mstr.Read(decrpt, 0, decrpt.Length);
            return Encoding.UTF8.GetString(decrpt);
        }
    }
}

