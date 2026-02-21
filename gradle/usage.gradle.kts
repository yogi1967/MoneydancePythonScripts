/*
 * Author: Stuart Beesley - February 2026
 * usage.gradle.kts: gradle buildfile that simply displays usage information for this build set
 * This should not be run standalone
 * This is a gradle kotlin DSL file (i.e. not groovy)
 * */

if (!extra.has("executingMainBuild")) {
    throw GradleException("usage.gradle.kts must be applied from build.gradle.kts, not executed standalone!")
}

tasks.register("printUsage") {
    group = "INFO"
    description = "Display build usage information"
    doLast {
        logger.lifecycle("")
        logger.lifecycle("-------------------------------------------------------------------------------------------------------------------------")
        logger.lifecycle("Moneydance Gradle build - usage")
        logger.lifecycle("")
        logger.lifecycle("./gradlew verifyConfig         -> configuration + path checks (default)")
        logger.lifecycle("./gradlew <extensionname>      -> build & sign one extension - e.g. ")
        logger.lifecycle("./gradlew allPython            -> build all Python extensions")
        logger.lifecycle("./gradlew all                  -> build everything")
        logger.lifecycle("./gradlew clean                -> removes the dist folder, and all build/compiled files")
        logger.lifecycle("./gradlew cleanextensionname   -> cleanup a single extension's build files")
        logger.lifecycle("./gradlew ensureDist           -> ensure the dist folder is present (otherwise does nothing)")
        logger.lifecycle("./gradlew ensureUserConfig     -> ensure the userconfig folder is present (otherwise does nothing)")
        logger.lifecycle("./gradlew ensureUserProperties -> creates user.gradle.properties file/template if missing (otherwise does nothing)")
        logger.lifecycle("./gradlew genKeys              -> generate signing keys - see below...")
        logger.lifecycle("")
        logger.lifecycle("Configuration files (in order of precedence):")
        logger.lifecycle("  userconfig/user.gradle.properties   (user overrides - not committed to git)")
        logger.lifecycle("  gradle.properties                   (base set of properties - committed to git)")
        logger.lifecycle("")
        logger.lifecycle("Signing setup:")
        logger.lifecycle("  Set keypass=<your passphrase> in user.gradle.properties")
        logger.lifecycle("  Then run: ./gradlew genKeys")
        logger.lifecycle("")
        logger.lifecycle("Optional flags (user.gradle.properties):")
        logger.lifecycle("  debug=true                   -> enable additional debug messages")
        logger.lifecycle("  md_ext_lib_dir=<folder>      -> specify folder containing a 'master set' of Moneydance jars (overriding lib folder jars)")
        logger.lifecycle("")
        logger.lifecycle("-------------------------------------------------------------------------------------------------------------------------")
        logger.lifecycle("")
    }
}