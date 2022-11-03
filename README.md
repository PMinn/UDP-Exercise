# 網路程式設計

## Lab 5-2 UDP Exercise

為了解決 UDP 封包在傳送過程中可能會遺失的問題，SAWSocket.py 實作了 Stop-and-wait 的 Flow control 機制。但我們知道 Stop-and wait 的效率不佳，所以請修改 SAWSocket.py 及相關 Client/Server程式，讓我們可以從 Server 的命令列參數中填入 Sliding windows 的值 w，讓送方可以連續送出 w 個封包，收方才回一個 ACK。請注意，收方仍要有 timeout 的機制以解決送方沒有送滿 w 個封包，而收方一直不回 ACK 的問題。
