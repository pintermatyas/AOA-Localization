package hu.bme.aut.android.bluetoothpositioning

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun NavGraph(
    navController: NavHostController = rememberNavController(),
) {
    NavHost(
        navController = navController,
        startDestination = "MenuScreen"
    ) {
        composable("MenuScreen") {
            MenuScreen(
                navController,
                onConfigButton = { navController.navigate("ImageSelectionScreen") },
                onMapButton = { navController.navigate("ReceivedPacketView") }
            )
        }
        composable("ReceivedPacketView") {
            ReceivedPacketView(navController)
        }
        composable("ImageSelectionScreen") {
            ImageSelectionScreen(
                navController,
                onConfirm = { image, topRightCoordinate, bottomLeftCoordinate ->
                    navController.navigate("MenuScreen") {
                        popUpTo("ImageSelectionScreen") { inclusive = true }
                    }
                }
            )
        }
    }
}
