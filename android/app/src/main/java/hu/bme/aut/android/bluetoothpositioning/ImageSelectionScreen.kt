package hu.bme.aut.android.bluetoothpositioning

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import java.io.File
import java.io.FileInputStream
import java.io.IOException

@Composable
fun ImageSelectionScreen() {
    val context = LocalContext.current
    val imageBitmap = remember { mutableStateOf<Bitmap?>(null) }
    imageBitmap.value = loadImageFromInternalStorage(context)

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent(),
        onResult = { uri: Uri? ->
            saveImageToInternalStorage(context, uri!!)
            imageBitmap.value = loadImageFromInternalStorage(context)
        }
    )

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(
            onClick = {
                launcher.launch("image/*")
            }
        ) {
            Text(text = "Select Image")
        }

        imageBitmap.value?.let { bitmap ->
            Image(
                modifier = Modifier.fillMaxSize(),
                bitmap = bitmap.asImageBitmap(),
                contentDescription = "some useful description",
                contentScale = ContentScale.Fit,
            )
        }
    }

}

fun saveImageToInternalStorage(context: Context, uri: Uri) {
    val inputStream = context.contentResolver.openInputStream(uri)
    val outputStream = context.openFileOutput("image.jpg", Context.MODE_PRIVATE)
    inputStream?.use { input ->
        outputStream.use { output ->
            input.copyTo(output)
        }
    }
}

fun loadImageFromInternalStorage(context: Context): Bitmap? {
    try {
        val file = File(context.filesDir, "image.jpg")
        if (file.exists()) {
            val inputStream = FileInputStream(file)
            return BitmapFactory.decodeStream(inputStream)
        }
    } catch (e: IOException) {
        e.printStackTrace()
    }
    return null
}
