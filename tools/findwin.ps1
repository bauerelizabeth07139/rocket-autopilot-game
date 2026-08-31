Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

[StructLayout(LayoutKind.Sequential)]
public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

public class WinFinder {
    public delegate bool EWProc(IntPtr hwnd, IntPtr lparam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EWProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
}
"@

int myPid = 7928;
WinFinder.EWProc callback = (h, l) => {
    if(!WinFinder.IsWindowVisible(h)) return true;
    int pidVal = 0;
    WinFinder.GetWindowThreadProcessId(h, out pidVal);
    var sb = new StringBuilder(256);
    WinFinder.GetWindowText(h, sb, sb.Capacity);
    string txt = sb.ToString();
    if(pidVal == myPid) {
        Console.WriteLine("TARGET HWND=" + h.ToInt64() + " TITLE=" + txt);
    } else if(txt.Length > 5 && (txt.Contains("Rocket") || txt.Contains("火箭") || txt.Contains("Autopilot"))) {
        Console.WriteLine("FOUND HWND=" + h.ToInt64() + " PID=" + pidVal + " TITLE=" + txt);
    }
    return true;
};
WinFinder.EnumWindows(callback, IntPtr.Zero);
