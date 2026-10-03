plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.chaquo.python")
}

android {
    namespace = "org.christmanai.awarenistic"
    compileSdk = 34

    defaultConfig {
        applicationId = "org.christmanai.awarenistic"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        ndk {
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

// Her mind is her own files at the root of this repo, copied in at build time and
// never rewritten. One Awarenistic, not two.
val herMind = layout.buildDirectory.dir("her-mind")
val copyHerMind by tasks.registering(Copy::class) {
    from(rootProject.projectDir.parentFile) {
        include("SOUL.py", "SAFETY.py", "CORE.py", "VOICE.py", "MEMORY.py", "CHECKS.py")
    }
    into(herMind)
}

chaquopy {
    defaultConfig {
        version = "3.12"
        pyc {
            src = false
        }
    }
    sourceSets {
        getByName("main") {
            srcDir(herMind)
        }
    }
}

tasks.named("preBuild") {
    dependsOn(copyHerMind)
}
