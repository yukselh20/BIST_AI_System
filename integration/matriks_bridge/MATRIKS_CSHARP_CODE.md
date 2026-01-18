# Matriks IQ C# Entegrasyon Kodu

Bu kod bloğu, Matriks IQ terminali içerisindeki "Script" veya "Indicator" modüllerinde kullanılarak systemimize veri göndermek için tasarlanmıştır.

## Gereksinimler
- System.Net.Sockets
- Newtonsoft.Json (Eğer Matriks içinde mevcutsa, yoksa string formatlama kullanılabilir)

## C# Kodu

```csharp
using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class DataSender
{
    private TcpClient client;
    private NetworkStream stream;
    private const string SERVER_IP = "127.0.0.1";
    private const int SERVER_PORT = 5555;

    public void Connect()
    {
        try
        {
            client = new TcpClient(SERVER_IP, SERVER_PORT);
            stream = client.GetStream();
        }
        catch (Exception e)
        {
            // Matriks log penceresine yazılabilir
            // Debug.WriteLine("Bağlantı hatası: " + e.Message);
        }
    }

    public void SendData(string symbol, double price, DateTime time)
    {
        if (client == null || !client.Connected)
        {
            Connect();
        }

        if (client != null && client.Connected)
        {
            try
            {
                // Basit JSON formatı oluşturma
                string json = string.Format("{{\"symbol\": \"{0}\", \"price\": {1}, \"timestamp\": \"{2}\"}}\n", 
                                          symbol, 
                                          price.ToString(System.Globalization.CultureInfo.InvariantCulture), 
                                          time.ToString("o"));

                byte[] data = Encoding.UTF8.GetBytes(json);
                stream.Write(data, 0, data.Length);
            }
            catch (Exception e)
            {
                // Gönderim hatası
            }
        }
    }

    public void Close()
    {
        if (stream != null) stream.Close();
        if (client != null) client.Close();
    }
}
```

## Kullanım Notları
1. Bu sınıfı Matriks strateji dosyanızın global alanına ekleyin.
2. `OnInit` veya benzeri başlatma fonksiyonunda `Connect()` metodunu çağırın.
3. `OnDataUpdate` veya her tick geldiğinde `SendData(...)` metodunu çağırın.
