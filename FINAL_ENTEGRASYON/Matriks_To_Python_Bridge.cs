using System;
using System.Collections.Generic;
using System.Linq;
using Matriks.Data.Symbol;
using Matriks.Engines;
using Matriks.Indicators;
using Matriks.Symbols;
using Matriks.AlgoAccess;
using Matriks.Trader.Core;
using Matriks.Trader.Core.Fields;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json; // Newtonsoft.Json kütüphanesinin ekli oldugundan emin olun

namespace Matriks.IP.Algoritmalar
{
    public class PythonBridge : MatriksAlgo
    {
        // Strateji değişkenleri
        string Symbol = "THYAO";
        TcpClient client;
        NetworkStream stream;
        bool isConnected = false;

        [SymbolParameter("THYAO")]
        public string Symbol1;

        public override void OnInit()
        {
            AddSymbol(Symbol1, SymbolPeriod.Min);

            // Socket Bağlantısını Başlat
            ConnectToPython();

            // Opsiyonel: Log
            Debug("Matriks-Python Köprüsü Başlatıldı.");
        }

        public void ConnectToPython()
        {
            try
            {
                client = new TcpClient("127.0.0.1", 5555);
                stream = client.GetStream();
                isConnected = true;
                Debug("Python Sunucusuna Bağlanıldı.");
            }
            catch (Exception ex)
            {
                isConnected = false;
                Debug("Bağlantı Hatası: " + ex.Message);
            }
        }

        public override void OnDataUpdate(BarDataCurrentValues barData)
        {
            if (!isConnected)
            {
                // Bağlantı koptuysa tekrar dene
                ConnectToPython();
                if (!isConnected) return;
            }

            try
            {
                // JSON Verisini Oluştur
                // { "symbol": "THYAO", "price": 123.45, "volume": 5000, "timestamp": "..." }
                var data = new
                {
                    symbol = Symbol1,
                    price = barData.LastPrice,
                    volume = barData.LastVolume, // veya Toplam Hacim istenirse barData.TotalVolume
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                    source = "MatriksIQ"
                };

                string jsonString = JsonConvert.SerializeObject(data);
                
                // Mesajı Gönder (Sonuna satır sonu ekleyerek)
                byte[] bytes = Encoding.ASCII.GetBytes(jsonString + "\n");
                stream.Write(bytes, 0, bytes.Length);
            }
            catch (Exception ex)
            {
                Debug("Veri Gönderim Hatası: " + ex.Message);
                isConnected = false; // Hata durumunda bağlantıyı düşmüş farz et
            }
        }

        public override void OnStopped()
        {
            if (client != null)
            {
                stream.Close();
                client.Close();
            }
            Debug("Sistem Durduruldu.");
        }
    }
}
