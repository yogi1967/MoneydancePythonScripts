// Copyright (c) 2021 Stuart Beesley - StuWareSoftSystems - MIT License
// Purpose: Java code for use in Moneydance Jython scripts where simply not possible in pure Python/Jython
//          Bundled into the mxt(jar) file and use moneydance_extension_loader.loadClass() or java.net.URLClassLoader
//          No package name used as I want this in the root of the mxt(jar) so the MD signing routines keep it in the correct place.

//package stuwaresoftsystems.code;

@SuppressWarnings("unused")
public class StuWareSoftSystems_CommonCode {

    public static final String codeVersion = "0.4";
    public static boolean codeInstantiated = false;

    public static boolean test() {
        return test("");
    }
    public static boolean test(String name) {
        if (name == null) name = "";
        System.err.println("StuWareSoftSystems_CommonCode: test method... >> Hello " + name + " from your very own Java code");
        return (true);
    }

}
