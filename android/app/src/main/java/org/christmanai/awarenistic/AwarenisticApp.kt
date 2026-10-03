package org.christmanai.awarenistic

import android.app.Application
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

/** Wakes her mind once, on the phone, when the app starts. */
class AwarenisticApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        Her.makeChannel(this)
    }
}
