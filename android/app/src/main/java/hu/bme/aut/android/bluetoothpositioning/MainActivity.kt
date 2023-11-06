package hu.bme.aut.android.bluetoothpositioning

import android.Manifest
import android.app.Activity
import android.content.ContentValues.TAG
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.core.app.ActivityCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.BindException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress


class MainActivity : ComponentActivity() {

    private val REQUEST_EXTERNAL_STORAGE = 1
    private val PERMISSIONS_STORAGE = arrayOf(
        Manifest.permission.READ_EXTERNAL_STORAGE,
        Manifest.permission.WRITE_EXTERNAL_STORAGE
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        verifyStoragePermissions(this)
        setContent {
            MyApp {
                ReceivedPacketView()
            }
        }
        sendUdpMessage("Subscribe", 9903)
    }

    override fun onResume() {
        super.onResume()
        sendUdpMessage("Subscribe", 9903)
    }
    override fun onPause() {
        super.onPause()
        sendUdpMessage("Unsubscribe", 9903)
    }

    override fun onStop() {
        super.onStop()
        // Send "Unsubscribe" when closing the app
        sendUdpMessage("Unsubscribe", 9903)
    }

    override fun onRestart() {
        super.onRestart()
        // Resubscribe if the application is opened again from the background
        sendUdpMessage("Subscribe", 9903)
    }

    private fun sendUdpMessage(message: String, port: Int) {
        Thread {
            try {
                val udpSocket = DatagramSocket()
                val serverAddr: InetAddress = InetAddress.getByName("10.42.0.1")
                val buf: ByteArray = message.toByteArray()
                val packet = DatagramPacket(buf, buf.size, serverAddr, port)
                udpSocket.send(packet)
                udpSocket.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    fun verifyStoragePermissions(activity: Activity?) {
        // Check if we have write permission
        val permission = ActivityCompat.checkSelfPermission(
            activity!!,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        )
        if (permission != PackageManager.PERMISSION_GRANTED) {
            // We don't have permission so prompt the user
            ActivityCompat.requestPermissions(
                activity,
                PERMISSIONS_STORAGE,
                REQUEST_EXTERNAL_STORAGE
            )
        }
    }
}

@Composable
fun MyApp(content: @Composable () -> Unit) {
    MaterialTheme {
        Surface {
            content()
        }
    }
}

@Composable
fun ReceivedPacketView() {
    var packetData by remember { mutableStateOf("Awaiting packet...") }

    val context = LocalContext.current
    LaunchedEffect(key1 = context) {
        CoroutineScope(Dispatchers.IO).launch {
            try{
                val socket = DatagramSocket(9902)
                val buffer = ByteArray(1024)
                val packet = DatagramPacket(buffer, buffer.size)

                while (true) {
                    socket.receive(packet)
                    val message = String(packet.data, 0, packet.length)
                    if(!message.contains("nan")){
                        packetData = message
                        Log.d(TAG, packetData)
                    } else {
                        Log.e(TAG, message)
                    }
                }

                socket.close()
            }
            catch (e: BindException){
                e.printStackTrace()
            }
        }
    }


    if (packetData.contains("Awaiting")){
        Text(text=packetData)
    }
    else{
        MapScreen(data = packetData)
    }
}
