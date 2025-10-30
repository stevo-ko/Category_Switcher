/*
// Author: stevo_ko , https://twitch.tv/stevo_ko , Discord: stevo_ko on the streamer.bot Server, Github: https://github.com/stevo-ko/Category_Switcher
// Contact: on the above mentioned social media, or per ping in the streamer.bot server in the Thread for this tool or per directmessage to username stefan571
//
// This code is licensed under the GNU General Public License Version 3 (GPLv3).
// 
// The GPLv3 is a free software license that ensures end users have the freedom to run,
// study, share, and modify the software. Key provisions include:
// 
// - Copyleft: Modified versions of the code must also be licensed under the GPLv3.
// - Source Code: You must provide access to the source code when distributing the software.
// - Credit: You must credit the original author of the software, by mentioning either contact e-mail or their social media.
// - No Warranty: The software is provided "as-is," without warranty of any kind.
// 
// For more details, see https://www.gnu.org/licenses/gpl-3.0.en.html.
// Credit: Base GUI Code by MustachedManiac - link to his Site: https://mustachedmaniac.com/
*/
using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.ComponentModel;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Navigation;
using System.Windows.Threading;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Media.Animation;
using System.Windows.Data;
using System.Globalization;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Text.RegularExpressions;
using System.IO.Compression;
using Markdig;
using Markdig.Wpf;
using ShapesPath = System.Windows.Shapes.Path;

public class CPHInline
{
    private static HttpClient _httpClient = null;
    private static Thread uiThread;
    private static Dispatcher uiDispatcher;
    private static ManualResetEvent dispatcherReady = new ManualResetEvent(false);
    private static Window currentWindow;
    private static string FolderPath;
    private static string configPath;
    private static string filePath;

    private static string tempPath;
    private static string LanguagePath;
    private static string settingsPath;
    private static string messagesPath;
    private static string imagesPath;
    private static string currentDirectory;
    private static string botsettingsPath;
    private static string LocalVersionFile;
    private static string currentLang;
    private string remoteProgramVersion;
    private string remoteSettingsVersion;
    private bool _cancelDownload = false;
    private bool _checkUpdateInvokedByButton = false;

    private bool HasUpdateImport = false;
    private bool AutoUpdate;
    private bool DidRun;
    private UpdateResult _lastUpdateResult;
    private VersionInfo _localVersion; 
    private List<int> _categorySwitcherPids = new List<int>();
    private string _expectedCategorySwitcherPath;
    private Dictionary<string, string> languageDict = new();
    public bool Execute()
    {
        // ==== DE:Aktueller Verzeichnispfad, in dem das Skript ausgeführt wird | EN:Current directory, where the script is executed ====
        currentDirectory = AppDomain.CurrentDomain.BaseDirectory;
        botsettingsPath = Path.Combine(currentDirectory, "data\\settings.json");
        // ==== DE: Pfad wo settings.json von streamer.bot liegt | EN: Path where settings.json from streamer.bot is located ====
        string json1 = File.ReadAllText(botsettingsPath);
        JObject botSettings = JObject.Parse(json1);
        // ==== DE: Parse Json und setze Argument für HTTP Server Url und Port | EN: Parse Json and set HTTP Server Url and Port ====
        JObject httpConfig = new JObject
        {
            ["address"] = botSettings["http"]?["address"] ?? "127.0.0.1",
            ["port"] = botSettings["http"]?["port"] ?? "2310"
        };
        string jsonArgument = httpConfig.ToString(Formatting.None).Replace("\"", "\\\""); // Anführungszeichen escapen
        CPH.SetArgument("bot http", $"\"{jsonArgument}\"");

        // ==== DE: String aus Golbaler Variable ziehen, wenn nicht vorhanden Script starten | EN: Get string/text from persisted global variable, if it is not available start script ====
        FolderPath = CPH.GetGlobalVar<string>("[STEVO] SettingsPath", true);
        if (string.IsNullOrWhiteSpace(FolderPath))
        {
            CPH.RunAction("[STEVO] Open Category Switcher", true);
            Thread.Sleep(10000); // 10.000 Millisekunden = 10 Sekunden
            FolderPath = CPH.GetGlobalVar<string>("[STEVO] SettingsPath", true);
        }
        CPH.TryGetArg<string>("IsUpdate", out string UpdateJson);
        if (!string.IsNullOrWhiteSpace(UpdateJson))
        {
        _lastUpdateResult = JsonConvert.DeserializeObject<UpdateResult>(UpdateJson);
        }

        // ==== DE: Definiere Pfade zu den Dateien | EN: Define paths to the files ====
        filePath = Path.Combine(FolderPath, "settings.xaml");
        configPath = Path.Combine(FolderPath, "config.json");
        //settingsPath = Path.Combine(FolderPath, "settings.json");
        messagesPath = Path.Combine(FolderPath, "messages.json");
        imagesPath = Path.Combine(FolderPath, "_internal", "Assets");
        LocalVersionFile = Path.Combine(FolderPath, "Version.json");
        _expectedCategorySwitcherPath = Path.Combine(FolderPath, "Category_Switcher.exe");
        //MessageBox.Show($"Image path:\n{imagesPath}", "Fertig", MessageBoxButton.OK, MessageBoxImage.Information);
        LanguagePath = "";
        EnsureUIThread();
        bool? dialogResult = false;
        if (currentWindow != null && currentWindow.IsVisible)
            return true;
        uiDispatcher.Invoke(() =>
        {
            try
            {
                //MessageBox.Show($"FolderPath: {FolderPath}\n" + $"SettingsFilePath: {filePath}\n" + $"ConfigPath: {configPath}\n" + $"LanguagePath: {LanguagePath}", "Verwendete Pfade", MessageBoxButton.OK, MessageBoxImage.Information);
                string xaml = File.ReadAllText(filePath);
                currentWindow = (Window)XamlReader.Parse(xaml);
                _ViewModel = new LanguageViewModel("en");
                currentWindow.DataContext = _ViewModel;
                LoadSettings(currentWindow);
                //update = true;
                
                // ===== DE: Wenn durch AutoUpdateCheck aktiviert wurde und Update verfügbar zeig direkt Update-Overlay =====
                // ===== EN: If AutoUpdateCheck is enabled and an update is available, show the update overlay          ===== 
                if (_lastUpdateResult != null)
                {
                    if (_lastUpdateResult.ProgramUpdate)
                    {                        
                        ((Grid)currentWindow.FindName("UpdateOverlay")).Visibility = Visibility.Visible;
                        ((TextBlock)currentWindow.FindName("YourVersionSettings")).Text = "v" + _lastUpdateResult.CurrentSettingsVersion;
                        ((TextBlock)currentWindow.FindName("YourVersionProgram")).Text = "v" + _lastUpdateResult.CurrentProgramVersion;                                             
                        ((TextBlock)currentWindow.FindName("UpdateVersionSetting")).Text = "v" + _lastUpdateResult.RemoteSettingsVersion;
                        ((TextBlock)currentWindow.FindName("UpdateVersionProgram")).Text = "v" + _lastUpdateResult.RemoteProgramVersion;
                        ((TextBlock)currentWindow.FindName("ArrowProgram")).Visibility = Visibility.Visible;
                        ((TextBlock)currentWindow.FindName("ArrowSettings")).Visibility = Visibility.Visible;
                        HasUpdateImport = _lastUpdateResult.HasUpdateImport;
                        //ArrowSettings = (TextBlock)window.FindName("ArrowSettings");
                        //ArrowSettings.Visibility = Visibility.Visible;
                        //UpdateSettingsVersion.Text = "v" + remoteSettingsVersion;
                        if (!string.IsNullOrWhiteSpace(_lastUpdateResult.Changelog))
                        {

                            var ChangelogBorder = (Border)currentWindow.FindName("Changelog");
                            ChangelogBorder.Visibility = Visibility.Visible;
                            var changelogBox = (RichTextBox)currentWindow.FindName("ChangelogMarkdown");
                            string markdown = NormalizeNestedDashLists(_lastUpdateResult.Changelog);
                            markdown = NormalizeMarkdown(markdown);
                            var emojiMap = BuildGitHubEmojiUrlMap();
                            SetMarkdownToRichTextBoxRich(changelogBox, markdown, emojiMap);
                            ((Button)currentWindow.FindName("btnUpdate")).Visibility = Visibility.Visible;
                            ((Button)currentWindow.FindName("btnGithub")).Visibility = Visibility.Visible;

                        }
                    ((Button)currentWindow.FindName("btnBackUpdate")).Visibility = Visibility.Collapsed;
                    //btnCheckUpdate_Click(this, new RoutedEventArgs());
                    }
                    else
                    {
                        ((Grid)currentWindow.FindName("SettingsOverlay")).Visibility = Visibility.Visible;
                    }
                }
                else
                {
                    // ==== DE: Kein UpdateResult vorhanden → direkt SettingsOverlay anzeigen | EN: No UpdateResult available → directly show SettingsOverlay ====
                    ((Grid)currentWindow.FindName("SettingsOverlay")).Visibility = Visibility.Visible;
                }

                // ==== DE: Eventhandler registrieren wie gehabt | EN: Register event handlers as needed ====
                currentWindow.Loaded += Window_Loaded;
                ((Grid)currentWindow.FindName("TitleBar")).MouseLeftButtonDown += Window_MouseLeftButtonDown;

                //Language Things
                ((Button)currentWindow.FindName("btnEnglish")).Click += btnEnglish_Click;
                ((Button)currentWindow.FindName("btnGerman")).Click += btnGerman_Click;
                ((Button)currentWindow.FindName("btnGerman")).MouseEnter += Button_MouseEnter;
                ((Button)currentWindow.FindName("btnEnglish")).MouseEnter += Button_MouseEnter;
                ((Button)currentWindow.FindName("btnGerman")).MouseLeave += Button_MouseLeave;
                ((Button)currentWindow.FindName("btnEnglish")).MouseLeave += Button_MouseLeave;

                // Twitch Auth things
                ((PasswordBox)currentWindow.FindName("ClientIDHideBox")).PasswordChanged += ClientIDHideBox_PasswordChanged;
                ((ToggleButton)currentWindow.FindName("ClientIDToggle")).Click += ClientIDToggle_Click;
                ((PasswordBox)currentWindow.FindName("TokenHideBox")).PasswordChanged += TokenHideBox_PasswordChanged;
                ((ToggleButton)currentWindow.FindName("TokenToggle")).Click += TokenToggle_Click;

                //Window Buttons
                ((Button)currentWindow.FindName("btnMinimize")).Click += BtnMinimize_Click;
                ((Button)currentWindow.FindName("btnClose")).Click += BtnClose_Click;
                ((Button)currentWindow.FindName("btnAbout")).Click += BtnAbout_Click;
                ((Button)currentWindow.FindName("btnBack")).Click += BtnBack_Click;
                ((Button)currentWindow.FindName("btnSave")).Click += btnConfirmSave_Click;
                ((Button)currentWindow.FindName("btnDiscord")).Click += BtnDiscord_Click;

                //Excluded Name List + Buttons and Popup
                ((ToggleButton)currentWindow.FindName("toggleNames")).Unchecked += Toggle_Unchecked;
                ((Button)currentWindow.FindName("btnExeNamePopup")).Click += AddNameButton_Click;
                ((Button)currentWindow.FindName("btnCancelAdd")).Click += OnCancelClick;
                ((Button)currentWindow.FindName("btnExeName")).Click += AddExeName_Click;
                ((TextBox)currentWindow.FindName("ExeNameBox")).TextChanged += ExeNameBox_TextChanged;
                ((TextBox)currentWindow.FindName("ExeNameBox")).KeyDown += ExeNameBox_Enter
                ;
                //Excluded Folder + Allowed Paths + Buttons and Popup             
                ((ToggleButton)currentWindow.FindName("toggleAllowedPaths")).Unchecked += Toggle_Unchecked; 
                ((ToggleButton)currentWindow.FindName("toggleExcludedFolders")).Unchecked += Toggle_Unchecked;  
                ((Button)currentWindow.FindName("btnAddFolderNamePopup")).Click += AddFolderNamePopup_Click;
                ((Button)currentWindow.FindName("btnAddPathPopup")).Click += AddFolderPathPopup_Click;
                ((Button)currentWindow.FindName("btnConfirmAddFolderName")).Click += btnConfirmAddFolderName_Click;
                ((Button)currentWindow.FindName("btnCancelAddFolderName")).Click += btnCancelAddFolderName_Click;
                ((Button)currentWindow.FindName("btnConfirmAddFolderPath")).Click += btnConfirmAddFolderPath_Click;
                ((Button)currentWindow.FindName("btnCancelAddFolderPath")).Click += btnCancelAddFolderPath_Click;
                ((TreeView)currentWindow.FindName("FolderTreeView")).SelectedItemChanged += (s, e) => FolderTreeView_SelectedItemChanged(s, e, "Name");
                ((TreeView)currentWindow.FindName("FolderTreeViewPath")).SelectedItemChanged += (s, e) => FolderTreeView_SelectedItemChanged(s, e, "Path");
                ((TreeView)currentWindow.FindName("DriveTreeView")).SelectedItemChanged += (s, e) => DriveTreeView_SelectedItemChanged(s, e, "Name");
                ((TreeView)currentWindow.FindName("DriveTreeViewPath")).SelectedItemChanged += (s, e) => DriveTreeView_SelectedItemChanged(s, e, "Path");

                //Delete Entries
                ((Button)currentWindow.FindName("btnDelAllowedPath")).Click += Delete_Click;
                ((Button)currentWindow.FindName("btnDelExcludedFolders")).Click += Delete_Click;
                ((Button)currentWindow.FindName("btnDelete")).Click += Delete_Click;
                ((Button)currentWindow.FindName("btnConfirmDelete")).Click += btnConfirmDelete_Click;
                ((Button)currentWindow.FindName("btnAbortDelete")).Click += btnAbortDelete_Click;

                //Warning Popup
                ((Button)currentWindow.FindName("btnWarningYes")).Click += btnWarningYes_Click;
                ((Button)currentWindow.FindName("btnWarningNo")).Click += btnWarningNo_Click;

                //Enable Popups to be dragged on screen
                ((Grid)currentWindow.FindName("AddFolderNameDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("AddFolderNameDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("AddFolderNameDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;
                ((Grid)currentWindow.FindName("AddFolderPathDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("AddFolderPathDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("AddFolderPathDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;
                ((Grid)currentWindow.FindName("ExeNameAddDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("ExeNameAddDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("ExeNameAddDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;
                ((Grid)currentWindow.FindName("SavePopupDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("SavePopupDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("SavePopupDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;
                ((Grid)currentWindow.FindName("WarningPopupDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("WarningPopupDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("WarningPopupDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;
                ((Grid)currentWindow.FindName("DeleteDragArea")).MouseLeftButtonDown += PopupHeaderDragArea_MouseLeftButtonDown1;
                ((Grid)currentWindow.FindName("DeleteDragArea")).MouseLeftButtonUp += PopupHeaderDragArea_MouseLeftButtonUp;
                ((Grid)currentWindow.FindName("DeleteDragArea")).MouseMove += PopupHeaderDragArea_MouseMove;

                //BoxArtSlider
                ((Slider)currentWindow.FindName("sldBoxSize")).ValueChanged += sldBoxSize_ValueChanged;

                //Save Popup
                ((Button)currentWindow.FindName("btnConfirmSave")).Click += btnConfirmSave_Click;
                ((Button)currentWindow.FindName("btnAbortSave")).Click += btnAbortSave_Click;

                //Hyperlinks
                ((Hyperlink)currentWindow.FindName("Icons8Link")).RequestNavigate += Hyperlink_RequestNavigate;
                ((Hyperlink)currentWindow.FindName("hyperlink")).RequestNavigate += Hyperlink_RequestNavigate;

                //AutoUpdateToggle
                ((CheckBox)currentWindow.FindName("AutoUpdateCheckbox")).Click += ToggleAutoUpdate;
                
                //Update Overlay
                ((Button)currentWindow.FindName("btnCheckUpdate")).Click += btnCheckUpdate_Click;
                ((Button)currentWindow.FindName("btnCancelDownload")).Click += btnCancelDownload_Click;
                ((Button)currentWindow.FindName("btnUpdate")).Click += btnUpdate_Click;
                ((Button)currentWindow.FindName("btnGithub")).Click += btnGithub_Click;
                ((Button)currentWindow.FindName("btnBackUpdate")).Click += BtnBack_Click;
                currentWindow.Topmost = true;
                dialogResult = currentWindow.ShowDialog();
                currentWindow = null;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Fehler beim Laden der XAML-Datei: " + ex.Message);
            }
        });
        return dialogResult.HasValue && dialogResult.Value;
    }

    private static void EnsureUIThread()
    {
        if (uiThread == null || !uiThread.IsAlive)
        {
            dispatcherReady.Reset();
            uiThread = new Thread(() =>
            {
                Application app = new Application
                {
                    ShutdownMode = ShutdownMode.OnExplicitShutdown
                };
                uiDispatcher = Dispatcher.CurrentDispatcher;
                dispatcherReady.Set();
                Dispatcher.Run();
            });
            uiThread.SetApartmentState(ApartmentState.STA);
            uiThread.IsBackground = true;
            uiThread.Start();
            dispatcherReady.WaitOne();
        }
    }

    ///
    /// ||=============================================================================================================================||
    /// || ====== DE: Lade Icons für Grund Fenster/About und Update aus Lokaler Datei, wenn nicht vorhanden downloade die Icons ====== ||
    /// || ======      EN: Load Icons for Base Window/About and Update from local file, if not present download the Icons       ====== ||
    /// ||=============================================================================================================================||
    ///  
    private async void LoadingIcons()
    {
        // ==== DE: Alle Tags sammeln und anzeigen | EN: Collect all tags and display them ====
        var tags = new List<string>();
        foreach (var image in FindVisualChildren<Image>(currentWindow))
        {
            if (image is FrameworkElement fe)
            {
                string tag = fe.Tag as string;
                if (!string.IsNullOrWhiteSpace(tag))
                {
                    tags.Add(tag);
                }
                else
                {
                    tags.Add("[leer or null]");
                }
            }
        }


        //MessageBox.Show("Gefundene Tags:\n" + string.Join("\n", tags), "Debug Tags");
        
        // ==== DE: Icons laden mit Debug-Ausgaben | EN: Load icons with debug output ====
        foreach (var image in FindVisualChildren<Image>(currentWindow))
        {
            if (image is FrameworkElement fe && fe.Tag is string tag && !string.IsNullOrWhiteSpace(tag))
            {
                string targetPath = Path.Combine(FolderPath, tag.Replace("/", "\\"));
                if (!File.Exists(targetPath))
                {
                    //MessageBox.Show($"Bild nicht gefunden:\n{targetPath}\nVersuche Download...", "Debug");
                    try
                    {
                        string downloadUrl = image.Source?.ToString();
                        if (image.Tag is string tagPath)
                        {
                            string fileName = Path.GetFileName(tagPath); // z.B. "Flag_Ger.png"
                            switch (fileName.ToLower())
                            {
                                case "flag_ger.png":
                                    downloadUrl = "https://img.icons8.com/?size=100&id=vRrbNnaD93Ys&format=png&color=000000";
                                    break;
                                case "flag_eng.png":
                                    downloadUrl = "https://img.icons8.com/?size=100&id=ShNNs7i8tXQF&format=png&color=000000";
                                    break;
                            }
                        }

                        //MessageBox.Show($"Source.ToString() ergibt:\n{downloadUrl}", "Download-URL");
                        if (!string.IsNullOrWhiteSpace(downloadUrl) && downloadUrl.StartsWith("http", StringComparison.OrdinalIgnoreCase))
                        {
                            string dir = Path.GetDirectoryName(targetPath);
                            if (!Directory.Exists(dir))
                            {
                                Directory.CreateDirectory(dir);
                                //MessageBox.Show($"Verzeichnis erstellt:\n{dir}", "Info");
                            }

                            using (var client = new System.Net.Http.HttpClient())
                            {
                                //MessageBox.Show("Starte Download...", "Download");
                                byte[] imageBytes = client.GetByteArrayAsync(downloadUrl).Result;
                                File.WriteAllBytes(targetPath, imageBytes);
                                //MessageBox.Show($"Download abgeschlossen:\n{targetPath}", "Download");
                            }
                        }
                        else
                        {
                            //MessageBox.Show("Ungültige oder leere Download-URL.", "Fehler");
                        }
                    }
                    catch (Exception ex)
                    {
                        //MessageBox.Show($"Fehler beim Herunterladen:\n{ex.Message}", "Fehler");
                    }
                }
                else
                {
                    // MessageBox.Show($"Bild lokal vorhanden:\n{targetPath}", "Info");
                }

                // ==== DE: Quelle setzen nur, wenn kein Flag-Bild | EN: Set source only if it is not a flag image ====
                if (tag.IndexOf("Flag", StringComparison.OrdinalIgnoreCase) == -1)
                {
                    try
                    {
                        image.Source = new BitmapImage(new Uri(targetPath, UriKind.Absolute));
                        //MessageBox.Show($"Bild erfolgreich geladen:\n{targetPath}", "Debug Loading Icons");
                    }
                    catch (Exception ex)
                    {
                        //MessageBox.Show($"Fehler beim Laden des Bildes:\n{targetPath}\nFehler: {ex.Message}", "Debug Loading Icons");
                    }
                }
                else
                {
                    //MessageBox.Show($"Flag-Image gefunden, Source wird NICHT gesetzt:\n{tag}", "Info");
                }
            }
        }   
    }

    ///
    /// ||=====================================================================================================||
    /// || ====== DE: Lade Icons für Popups aus Lokaler Datei, wenn nicht vorhanden downloade die Icons ====== ||
    /// || ======     EN: Load Icons for Popups from Local File, if not present download the Icons      ====== ||
    /// ||=====================================================================================================||
    ///  
    private async void LoadPopupIcons(Popup popup)
    {
        var tags = new List<string>();
        foreach (var img in FindVisualChildren<Image>(popup.Child))
        {
            if (img is FrameworkElement fe && fe.Tag is string tag && !string.IsNullOrWhiteSpace(tag))
            {
                tags.Add(tag);
                string targetPath = Path.Combine(FolderPath, tag.Replace("/", "\\"));
                if (!File.Exists(targetPath))
                {
                    try
                    {
                        string downloadUrl = img.Source?.ToString();
                        if (img.Tag is string tagPath)
                        {
                            string fileName = Path.GetFileName(tagPath); // z.B. "Flag_Ger.png"
                            //MessageBox.Show($"Tag: {tagPath}\nFileName: {Path.GetFileName(tagPath)}");
                            switch (fileName.ToLower())
                            {
                                case "checkmark.png":
                                    ExtractCheckmark("https://img.icons8.com/?size=100&id=70yRC8npwT3d&format=png&color=fff0000");
                                    continue;
                                case "cancel.png":
                                    ExtractCancel("https://img.icons8.com/?size=100&id=fYgQxDaH069W&format=png&color=000000");
                                    continue;
                            }
                        }                        
                        if (!string.IsNullOrWhiteSpace(downloadUrl) && downloadUrl.StartsWith("http", StringComparison.OrdinalIgnoreCase))
                        {
                            string dir = Path.GetDirectoryName(targetPath);
                            if (!Directory.Exists(dir))
                            {
                                Directory.CreateDirectory(dir);
                            }

                            using (var client = new System.Net.Http.HttpClient())
                            {
                                byte[] imageBytes = await client.GetByteArrayAsync(downloadUrl);
                                File.WriteAllBytes(targetPath, imageBytes);
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Fehler beim Herunterladen:\n{ex.Message}", "Fehler");
                    }
                }

                if (tag.IndexOf("Flag", StringComparison.OrdinalIgnoreCase) == -1)
                {
                    try
                    {
                        img.Source = new BitmapImage(new Uri(targetPath, UriKind.Absolute));
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Fehler beim Laden von {targetPath}: {ex.Message}", "Bildfehler");
                    }
                }
            }
        }

        if (tags.Count > 0)
        {
            //MessageBox.Show("Gefundene Tags:\n" + string.Join("\n", tags));
        }
        else
        {
        MessageBox.Show("Keine Tags gefunden.");
        }
    }

    /// 
    /// ||=========================================||
    /// || ====== DE: Extract Cancel Button ====== ||
    /// || ====== EN: Extract Cancel Button ====== ||
    /// ||=========================================||
    /// 
    static void ExtractCancel(string imageUrl)
    {
        try
        {
            Directory.CreateDirectory(imagesPath);
            string outputPath = Path.Combine(imagesPath, "cancel.png");

            byte[] imageBytes;
            using (WebClient client = new WebClient())
                imageBytes = client.DownloadData(imageUrl);
            BitmapImage bitmap = new BitmapImage();
            using (var ms = new MemoryStream(imageBytes))
            {
                bitmap.BeginInit();
                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.StreamSource = ms;
                bitmap.EndInit();
                bitmap.Freeze();
            }

            int width = bitmap.PixelWidth;
            int height = bitmap.PixelHeight;
            int stride = width * 4;
            byte[] pixelData = new byte[height * stride];
            bitmap.CopyPixels(pixelData, stride, 0);

            byte[] resultData = new byte[pixelData.Length];
            for (int i = 0; i < pixelData.Length; i += 4)
            {
                byte b = pixelData[i];
                byte g = pixelData[i + 1];
                byte r = pixelData[i + 2];
                byte a = pixelData[i + 3];

                bool isRedCircle = r > 180 && g < 100 && b < 100;
                if (!isRedCircle && a > 10)
                {
                    float alphaFactor = a / 255f;
                    resultData[i] = 0; // Blue
                    resultData[i + 1] = 0; // Green
                    resultData[i + 2] = 255; // Red
                    resultData[i + 3] = (byte)(alphaFactor * 255);
                }
                else
                {

                    resultData[i + 3] = 0;
                }
            }


            WriteableBitmap resultBmp = new WriteableBitmap(width, height, 96, 96, PixelFormats.Bgra32, null);
            resultBmp.WritePixels(new Int32Rect(0, 0, width, height), resultData, stride, 0);

            DrawingVisual dv = new DrawingVisual();
            using (DrawingContext dc = dv.RenderOpen())
            {
                dc.DrawRectangle(Brushes.Transparent, null, new Rect(0, 0, 100, 100));
                dc.DrawImage(resultBmp, new Rect(0, 0, 100, 100));
            }

            RenderTargetBitmap final = new RenderTargetBitmap(100, 100, 96, 96, PixelFormats.Pbgra32);
            final.Render(dv);
            using (FileStream fs = new FileStream(outputPath, FileMode.Create))
            {
                PngBitmapEncoder encoder = new PngBitmapEncoder();
                encoder.Frames.Add(BitmapFrame.Create(final));
                encoder.Save(fs);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show("Fehler: " + ex.Message, "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    ///
    /// ||============================================||
    /// || ====== DE: Extract Checkmark Button ====== ||
    /// || ====== EN: Extract Checkmark Button ====== ||
    /// ||============================================||
    ///     
    static void ExtractCheckmark(string imageUrl)
    {
        try
        {
            // Erstelle Ordner, falls noch nicht vorhanden
            Directory.CreateDirectory(imagesPath);
            string outputFileName = "checkmark.png";
            string outputPath = Path.Combine(imagesPath, outputFileName);
            // Bild laden
            byte[] imageBytes;
            using (WebClient client = new WebClient())
            {
                imageBytes = client.DownloadData(imageUrl);
            }

            BitmapImage bitmap = new BitmapImage();
            using (var ms = new MemoryStream(imageBytes))
            {
                bitmap.BeginInit();
                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.StreamSource = ms;
                bitmap.EndInit();
                bitmap.Freeze();
            }

            int width = bitmap.PixelWidth;
            int height = bitmap.PixelHeight;
            int stride = width * 4;
            byte[] pixelData = new byte[height * stride];
            bitmap.CopyPixels(pixelData, stride, 0);
            for (int i = 0; i < pixelData.Length; i += 4)
            {
                byte b = pixelData[i];
                byte g = pixelData[i + 1];
                byte r = pixelData[i + 2];
                byte a = pixelData[i + 3];
                if (r > 200 && g > 200 && b > 200)
                {
                    pixelData[i] = 0; // B
                    pixelData[i + 1] = 255;
                    pixelData[i + 2] = 0;
                    pixelData[i + 3] = a;
                }
                else
                {
                    pixelData[i + 3] = 0;
                }
            }

            WriteableBitmap writable = new WriteableBitmap(width, height, 96, 96, PixelFormats.Bgra32, null);
            writable.WritePixels(new Int32Rect(0, 0, width, height), pixelData, stride, 0);
            using (FileStream outStream = new FileStream(outputPath, FileMode.Create))
            {
                PngBitmapEncoder encoder = new PngBitmapEncoder();
                encoder.Frames.Add(BitmapFrame.Create(writable));
                encoder.Save(outStream);
            }
            //MessageBox.Show($"Bild erfolgreich extrahiert und gespeichert:\n{outputPath}", "Fertig", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
            //MessageBox.Show("Fehler: " + ex.Message, "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    ///
    /// ||==============================================================||
    /// || ====== DE: Lade Flags als Graustufen wenn nicht aktiv ====== ||
    /// || ======  EN: Load Flags as Grayscale when not acitve   ====== ||
    /// ||==============================================================||
    ///  
    public static ImageSource LoadImageAsGrayscale(string pathOrUrl)
    {
        //MessageBox.Show("LoadImageAsGrayscale gestartet: " + pathOrUrl);
        //MessageBox.Show(pathOrUrl);
        byte[] data;
        if (Uri.IsWellFormedUriString(pathOrUrl, UriKind.Absolute))
        {
            //MessageBox.Show("Pfad ist URL, lade mit WebClient");
            using var webClient = new WebClient();
            data = webClient.DownloadData(pathOrUrl);
        //MessageBox.Show("Download abgeschlossen");
        }
        else
        {
            //MessageBox.Show("Pfad ist lokale Datei, lade von Festplatte");
            data = File.ReadAllBytes(pathOrUrl);
        //MessageBox.Show("Datei geladen");
        }

        using var stream = new MemoryStream(data);
        var decoder = new PngBitmapDecoder(stream, BitmapCreateOptions.PreservePixelFormat, BitmapCacheOption.OnLoad);
        var bitmap = decoder.Frames[0];
        int width = bitmap.PixelWidth;
        int height = bitmap.PixelHeight;
        int stride = width * 4;
        byte[] pixelData = new byte[height * stride];
        bitmap.CopyPixels(pixelData, stride, 0);
        //MessageBox.Show("Pixel kopiert, starte Graustufen-Konvertierung");
        for (int i = 0; i < pixelData.Length; i += 4)
        {
            byte r = pixelData[i + 2];
            byte g = pixelData[i + 1];
            byte b = pixelData[i];
            byte a = pixelData[i + 3];
            byte gray = (byte)((r * 0.3) + (g * 0.59) + (b * 0.11));
            pixelData[i] = gray;
            pixelData[i + 1] = gray;
            pixelData[i + 2] = gray;
            pixelData[i + 3] = a;
        }

        //MessageBox.Show("Graustufen-Konvertierung abgeschlossen");
        var grayBitmap = BitmapSource.Create(width, height, bitmap.DpiX, bitmap.DpiY, PixelFormats.Bgra32, null, pixelData, stride);
        grayBitmap.Freeze();
        //MessageBox.Show("Bitmap erstellt und gefroren");
        return grayBitmap;
    }

    ///
    /// ||==================================================||
    /// || ==== DE: Setze Image Sources aus den Tags ====== ||
    /// || ====  EN: Set Image Sources from the Tags ====== ||
    /// ||==================================================||
    /// 
    void SetImageSources(DependencyObject root)
    {
        foreach (var child in FindVisualChildren<Image>(root))
        {
            if (child.Tag is string path)
            {
                string fullPath = Path.Combine(FolderPath, path);
                if (File.Exists(fullPath))
                {
                    child.Source = new BitmapImage(new Uri(fullPath));
                }
            }
        }
    }

    private T? FindChild<T>(DependencyObject parent, string childName)
        where T : FrameworkElement
    {
        if (parent == null)
        {
            //MessageBox.Show("🔴 Parent is null.");
            return null;
        }

        for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
        {
            var child = VisualTreeHelper.GetChild(parent, i);
            if (child is FrameworkElement fe)
            {
                if (fe.Name == childName && child is T correctlyTyped)
                {
                    //MessageBox.Show($"✅ Gefunden: {typeof(T).Name} mit Name '{childName}'");
                    return correctlyTyped;
                }
            }

            var result = FindChild<T>(child, childName);
            if (result != null)
                return result;
        }

        // Nur einmal zeigen, wenn nichts gefunden wurde (aber nur ganz am Ende)
        if (parent is Popup)
        {
        //MessageBox.Show($"❌ Element mit Name '{childName}' vom Typ {typeof(T).Name} wurde NICHT gefunden.");
        }

        return null;
    }

    public static IEnumerable<T> FindVisualChildren<T>(DependencyObject depObj)
        where T : DependencyObject
    {
        if (depObj != null)
        {
            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(depObj); i++)
            {
                DependencyObject child = VisualTreeHelper.GetChild(depObj, i);
                if (child != null && child is T t)
                {
                    yield return t;
                }

                foreach (T childOfChild in FindVisualChildren<T>(child))
                {
                    yield return childOfChild;
                }
            }
        }
    }

    // Suche alle Images mit Tag in mehreren Wurzeln (z.B. Window und Popups)
    public static IEnumerable<Image> FindImagesWithTag(params DependencyObject[] roots)
    {
        foreach (var root in roots)
        {
            if (root == null)
                continue;
            foreach (var img in FindVisualChildren<Image>(root))
            {
                if (img is FrameworkElement fe && fe.Tag != null)
                    yield return img;
            }
        }
    }

    /// 
    /// ||==============================================================||     
    /// || ====== DE: Laden der Einstellungen aus der JSON-Datei ====== || 
    /// || ======           EN: Load Settings from json          ====== ||
    /// ||==============================================================||
    ///
    private string originalSettingsJson = "";
    private void LoadSettings(Window window)
    {
        if (!File.Exists(configPath))
        {
            MessageBox.Show("Die Konfigurationsdatei wurde nicht gefunden.", "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
            return;
        }

        if (!File.Exists(botsettingsPath))
        {
            MessageBox.Show("Die Konfigurationsdatei von Streamer.bot wurde nicht gefunden.", "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
            return;
        }

        if (!File.Exists(LocalVersionFile))
        {
            MessageBox.Show("Die Versionsdatei wurde nicht gefunden.", "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
            return;
        }

        string json = File.ReadAllText(configPath);
        //streamer.bot settings.json path
        string json1 = File.ReadAllText(botsettingsPath);
        //originalSettingsJson = json;
        JObject stevoSettings = JObject.Parse(json);
        //from streamerbot settings.json 
        JObject botSettings = JObject.Parse(json1);

        //from localversionfile
        if (!File.Exists(LocalVersionFile))
        {
            MessageBox.Show("Version.json nicht gefunden!", "Debug", MessageBoxButton.OK, MessageBoxImage.Warning);
        }
        else
        {
        var localJson = File.ReadAllText(LocalVersionFile);
        _localVersion = JsonConvert.DeserializeObject<VersionInfo>(localJson);
        }

        // Streamer.bot-Adresse und Port in die Hauptkonfiguration übernehmen
        string httpAddress = botSettings["http"]?["address"]?.ToString();
        string httpPort = botSettings["http"]?["port"]?.ToString();
        // streamerbot-Objekt holen oder erzeugen
        var streamerbot = stevoSettings["streamerbot"] as JObject ?? new JObject();
        // In Hauptsettings setzen (falls vorhanden)
        streamerbot["url"] = httpAddress;
        streamerbot["port"] = httpPort;
        // Zurück in die Settings, falls vorher null
        stevoSettings["streamerbot"] = streamerbot;
        originalSettingsJson = stevoSettings.ToString(Formatting.Indented);
        var twitch = stevoSettings["twitch"] as JObject ?? new JObject();
        //var streamerbot = stevoSettings["streamerbot"] as JObject ?? new JObject();
        ((TextBox)window.FindName("StreamerBotUrl")).Text = streamerbot["url"]?.ToString() ?? "";
        ((TextBox)window.FindName("StreamerBotPort")).Text = streamerbot["port"]?.ToString() ?? "";
        var clientBox = (PasswordBox)window.FindName("ClientIDHideBox");
        var clientPlaceholder = (TextBlock)window.FindName("ClientIDPlaceholder");
        clientBox.Password = twitch["CLIENT_ID"]?.ToString() ?? "";
        UpdatePasswordPlaceholder(clientBox, clientPlaceholder);
        var tokenBox = (PasswordBox)window.FindName("TokenHideBox");
        var tokenPlaceholder = (TextBlock)window.FindName("TokenPlaceholder");
        tokenBox.Password = twitch["OAuth_token"]?.ToString() ?? "";
        UpdatePasswordPlaceholder(tokenBox, tokenPlaceholder);
        var paths = stevoSettings["paths"] as JObject ?? new JObject();
        var allowed_paths = paths["allowed_paths"] as JArray;
        var Allowed_Paths = (ListBox)window.FindName("Allowed_Paths");
        Allowed_Paths.Items.Clear();
        if (allowed_paths != null)
        {
            foreach (var item in allowed_paths)
            {
                Allowed_Paths.Items.Add(new ListBoxItem { Content = item.ToString() });
            }
        }

        var excluded_names = paths["excluded_names"] as JArray;
        var Excluded_Names = (ListBox)window.FindName("Excluded_Names");
        Excluded_Names.Items.Clear();
        if (excluded_names != null)
        {
            foreach (var item in excluded_names)
            {
                Excluded_Names.Items.Add(new ListBoxItem { Content = item.ToString() });
            }
        }

        var excluded_folders = paths["excluded_folders"] as JArray;
        var Excluded_Folders = (ListBox)window.FindName("Excluded_Folders");
        Excluded_Folders.Items.Clear();
        if (excluded_folders != null)
        {
            foreach (var item in excluded_folders)
            {
                Excluded_Folders.Items.Add(new ListBoxItem { Content = item.ToString() });
            }
        }

        var api = stevoSettings["api"] as JObject ?? new JObject();
        var options = stevoSettings["options"] as JObject ?? new JObject();
        // Language
        var language = stevoSettings["options"]?["language"]?.ToString();
        // Box Art Size
        var boxSize = stevoSettings["options"]?["Box_Art_Size"]?.ToString() ?? "285x380";
        var size = BoxSizeHelper.ParseSize(boxSize);
        var snappedSize = BoxSizeHelper.SnapToStandardBoxArtSize(size.Width, size.Height);
        int index = BoxSizeHelper.GetIndexOfSize(snappedSize);
        if (index == -1)
            index = 0;
        var sldBoxSize = (Slider)window.FindName("sldBoxSize");
        sldBoxSize.Minimum = 0;
        sldBoxSize.Maximum = BoxSizeHelper.StandardSizes.Count - 1;
        sldBoxSize.Value = index;
        UpdateBoxSizeDisplay(index);
        // Similarity
        ((Slider)window.FindName("sldSimilarity")).Value = options["similarity"]?.ToObject<int>() ?? 94;
        //Delays
        ((Slider)window.FindName("sldDelayGeneral")).Value = options["delay_general"]?.ToObject<int>() ?? 0;
        ((Slider)window.FindName("sldDelayProgramming")).Value = options["delay_programming"]?.ToObject<int>() ?? 60;
        ((Slider)window.FindName("sldDelayPlaynite")).Value = options["delay_playnite"]?.ToObject<int>() ?? 0;
        // Options
        ((ToggleButton)window.FindName("toggleWatchStreamerBot")).IsChecked = options["watch_streamerbot"]?.ToObject<bool>() ?? true;
        ((ToggleButton)window.FindName("toggleWatchOBS")).IsChecked = options["watch_obs"]?.ToObject<bool>() ?? false;
        ((ToggleButton)window.FindName("toggleOnlyLocalDb")).IsChecked = options["only_local_db"]?.ToObject<bool>() ?? false;
        ((ToggleButton)window.FindName("toggleShowConsole")).IsChecked = options["show_console"]?.ToObject<bool>() ?? true;
        // Chat message enable and options
        ((ToggleButton)window.FindName("toggleMessageEnabled")).IsChecked = options["message"]?.ToObject<bool>() ?? true;
        ((ToggleButton)window.FindName("toggleCensorMode")).IsChecked = options["censor_mode"]?.ToObject<bool>() ?? false;
        ((ToggleButton)window.FindName("toggleAsAnnouncement")).IsChecked = options["AsAnnouncement"]?.ToObject<bool>() ?? false;
        ((ToggleButton)window.FindName("toggleKick")).IsChecked = options["kick_enabled"]?.ToObject<bool>() ?? false;
        ((ToggleButton)window.FindName("togglePlaynite")).IsChecked = options["playnite_enabled"]?.ToObject<bool>() ?? false;

        HighlightLanguageButton(language);
    // Ausgabe zur Kontrolle
    //MessageBox.Show(originalSettingsJson);
    }

    ///     
    /// ||====================================================================================================||
    /// || ====== DE: Funktion zum Prüfen und setzen der Checkbox wenn AutoUpdate Action Aktiviert ist ====== ||
    /// || ======      EN: Function to check and set the checkbox if AutoUpdate Action is enabled      ====== ||
    /// ||====================================================================================================||
    /// 
    private void CheckAutoUpdate()
    {
        var window = Application.Current.MainWindow;
        var AutoUpd = (CheckBox)window.FindName("AutoUpdateCheckbox");
        AutoUpd.ApplyTemplate();
        if (AutoUpd != null)
        {
            // Alle Actions holen
            List<ActionData> actionList = CPH.GetActions();
            // Ziel-Action suchen
            ActionData targetAction = actionList.Find(a => a.Name == "[STEVO] Update Check");
            if (targetAction != null)
            {
                // Wert aus der Action
                AutoUpdate = targetAction.Enabled;
                //MessageBox.Show($"targetAction.Enabled = {targetAction.Enabled}", "Debug");
                // Checkbox setzen
                AutoUpd.IsChecked = AutoUpdate;
            //MessageBox.Show($"AutoUpd.IsChecked = {AutoUpd.IsChecked}", "Debug");
            }
            else
            {
                MessageBox.Show("Action '[STEVO] Update Check' nicht gefunden.", "Fehler");
            }
        }
        else
        {
            MessageBox.Show("Checkbox 'AutoUpdateCheckbox' nicht gefunden!", "Fehler");
        }
    }

    ///     
    /// ||=================================================================================||
    /// || ====== DE: Funktion zum Aktivieren/Deaktivieren der Auto-Update-Funktion ====== ||
    /// || ======      EN: Function to enable/disable the auto-update function      ====== ||
    /// ||=================================================================================||
    /// 
    private void ToggleAutoUpdate(object sender, RoutedEventArgs e)
    {
        if (AutoUpdate == true)
        {
            CPH.DisableAction("[STEVO] Update Check");
            AutoUpdate = false;
        }
        else
        {
            CPH.EnableAction("[STEVO] Update Check");
            AutoUpdate = true;
        }
    }

    ///
    /// ||=================================================||
    /// || ====== DE: Sprache wechseln zur Laufzeit ====== ||
    /// || ======  EN: Change language at runtime   ====== ||
    /// ||===================== Start =====================||
    ///
    private LanguageViewModel _ViewModel;
    public class LanguageViewModel : INotifyPropertyChanged
    {
        private Dictionary<string, string> _translations = new Dictionary<string, string>();
        public event PropertyChangedEventHandler PropertyChanged;
        private string CurrentLang = "en";
        public LanguageViewModel(string initialLang = "en")
        {
            LoadLanguage(initialLang);
        }
        public string currentLang          
        {
            get => CurrentLang;
            private set
            {
                if (CurrentLang != value)
                {
                    CurrentLang = value;
                    OnPropertyChanged(nameof(currentLang));
                }
            }
        }
        private Dictionary<string, string> FlattenJson(Dictionary<string, object> dict, string prefix = "")
        {
            var result = new Dictionary<string, string>();
            foreach (var kvp in dict)
            {
                string key = string.IsNullOrEmpty(prefix) ? kvp.Key : $"{prefix}.{kvp.Key}";
                if (kvp.Value is JObject nestedObj)
                {
                    // Falls es verschachtelt ist: rekursiv flatten
                    var nestedDict = nestedObj.ToObject<Dictionary<string, object>>();
                    foreach (var inner in FlattenJson(nestedDict, key))
                        result[inner.Key] = inner.Value;
                }
                else if (kvp.Value is JValue value)
                {
                    result[key] = value.ToString();
                }
                else
                {
                    // Für andere Typen
                    result[key] = kvp.Value?.ToString() ?? "";
                }
            }

            return result;
        }

        public string this[string key]
        {
            get
            {
                if (_translations.ContainsKey(key))
                {
                    return _translations[key];
                }

                return $"[{key}]"; // fallback
            }
        }

        public void SwitchLanguage(string newLang)
        {
            if (newLang == currentLang)
                return;
            currentLang = newLang;
            LoadLanguage(currentLang);
            OnPropertyChanged("Item[]");
        }

        public void LoadLanguage(string langCode)
        {
            LanguagePath = Path.Combine(FolderPath, "Resources", $"language_{langCode}.json");
            if (!File.Exists(LanguagePath))
                return;
            var json = File.ReadAllText(LanguagePath);
            var nestedDict = JsonConvert.DeserializeObject<Dictionary<string, object>>(json);
            _translations = FlattenJson(nestedDict);
            OnPropertyChanged("Item[]");
        }

        private void OnPropertyChanged(string propName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propName));
        }
    }

    private Button _activeLanguageButton;
    private void SetActiveLanguageButton(Button button)
    {
        // Vorherigen zurücksetzen
        if (_activeLanguageButton != null)
        {
            var oldText = FindLanguageTextBlock(_activeLanguageButton);
            if (oldText != null)
                oldText.Foreground = Brushes.Gray;
        }

        _activeLanguageButton = button;
        var newText = FindLanguageTextBlock(button);
        if (newText != null)
            newText.Foreground = Brushes.White;
    }

    private TextBlock FindLanguageTextBlock(Button button)
    {
        if (VisualTreeHelper.GetParent(button)is StackPanel stackPanel)
        {
            return stackPanel.Children.OfType<TextBlock>().FirstOrDefault();
        }

        return null;
    }

    private string currentLanguage = "";
    private void HighlightLanguageButton(string language)
    {
        var window = Application.Current.MainWindow;
        var btnEnglish = (Button)window.FindName("btnEnglish");
        var btnGerman = (Button)window.FindName("btnGerman");
        // Alles klein und getrimmt
        string lang = language?.Trim().ToLowerInvariant();
        currentLanguage = lang;
        string[] english =
        {
            "eng",
            "english",
            "englisch",
            "en"
        };
        string[] german =
        {
            "deu",
            "german",
            "deutsch",
            "ger",
            "de"
        };
        // Erst alle Umrandungen entfernen
        //ClearButtonHighlight(btnEnglish);
        //ClearButtonHighlight(btnGerman);
        string detected = "Unbekannte Sprache: " + (lang ?? "null");
        // Dann passende setzen
        if (english.Contains(lang))
        {
            SetActiveLanguageButton(btnEnglish);
            SetButtonHighlight(btnEnglish);
            _ViewModel.SwitchLanguage("en");
            detected = "English erkannt";
        }
        else if (german.Contains(lang))
        {
            SetActiveLanguageButton(btnGerman);
            SetButtonHighlight(btnGerman);
            _ViewModel.SwitchLanguage("de");
            detected = "Deutsch erkannt";
        }
    
    //MessageBox.Show(detected, "Sprache erkannt", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void SetButtonHighlight(Button button)
    {
        //MessageBox.Show($"SetButtonHighlight gestartet für {button.Name}");
        button.ApplyTemplate();
        var border = FindChild<Border>(button, "HighlightCircle");
        if (border != null)
        {
            //MessageBox.Show("HighlightCircle gefunden, setze Hintergrund auf LimeGreen");
            border.Background = Brushes.LimeGreen;
        }

        string imageName = (button.Name == "btnGerman") ? "GermanFlag" : "EnglishFlag";
        var image = FindChild<Image>(button, imageName);
        if (image != null)
        {
            //MessageBox.Show($"Image {imageName} gefunden");
            string localPath = Path.Combine(FolderPath, image.Tag as string ?? "");
            if (File.Exists(localPath))
            {
                //MessageBox.Show("Lokale Bilddatei gefunden: " + localPath);
                image.Source = new BitmapImage(new Uri(localPath));
            //MessageBox.Show("Bild gesetzt");
            }
            else
            {
                //MessageBox.Show("Lokale Bilddatei NICHT gefunden, verwende URL");
                string url = button.Name == "btnGerman" ? "https://img.icons8.com/?size=100&id=vRrbNnaD93Ys&format=png&color=000000" : "https://img.icons8.com/?size=100&id=ShNNs7i8tXQF&format=png&color=000000";
                image.Source = new BitmapImage(new Uri(url));
            //MessageBox.Show("Bild von URL gesetzt");
            }
        }

        var window = Application.Current.MainWindow;
        var otherButton = button.Name == "btnGerman" ? (Button)window.FindName("btnEnglish") : (Button)window.FindName("btnGerman");
        if (otherButton != null)
        {
            //MessageBox.Show($"Anderen Button gefunden: {otherButton.Name}");
            otherButton.ApplyTemplate();
            string otherImageName = otherButton.Name == "btnGerman" ? "GermanFlag" : "EnglishFlag";
            var otherImage = FindChild<Image>(otherButton, otherImageName);
            if (otherImage != null)
            {
                //MessageBox.Show($"Image {otherImageName} vom anderen Button gefunden");
                string otherLocalPath = Path.Combine(FolderPath, otherImage.Tag as string ?? "");
                if (File.Exists(otherLocalPath))
                {
                    //MessageBox.Show("Lokale Bilddatei für Graustufen gefunden: " + otherLocalPath);
                    otherImage.Source = LoadImageAsGrayscale(otherLocalPath);
                //MessageBox.Show("Graustufen-Bild gesetzt");
                }
                else
                {
                    //MessageBox.Show("Lokale Bilddatei für Graustufen NICHT gefunden, verwende URL");
                    string grayUrl = otherButton.Name == "btnGerman" ? "https://img.icons8.com/?size=100&id=vRrbNnaD93Ys&format=png&color=000000" : "https://img.icons8.com/?size=100&id=ShNNs7i8tXQF&format=png&color=000000";
                    otherImage.Source = LoadImageAsGrayscale(grayUrl);
                //MessageBox.Show("Graustufen-Bild von URL gesetzt");
                }
            }
            else
            {
            //MessageBox.Show($"Image {otherImageName} vom anderen Button NICHT gefunden");
            }

            var otherBorder = FindChild<Border>(otherButton, "HighlightCircle");
            if (otherBorder != null)
            {
                //MessageBox.Show("HighlightCircle beim anderen Button gefunden, setze Transparent");
                otherBorder.Background = Brushes.Transparent;
            }
        }
        else
        {
        //MessageBox.Show("Anderen Button NICHT gefunden");
        }
    //MessageBox.Show("SetButtonHighlight fertig");
    }

    private void ClearButtonHighlight(Button button)
    {
        var border = FindChild<Border>(button, "HighlightCircle");
        if (border != null)
            border.Background = Brushes.Transparent;
    }

    // == DE: Sprach Buttons (Flags) | EN: Language Buttons (Flags) ==
    private void btnGerman_Click(object sender, RoutedEventArgs e)
    {
        var language = "de";
        // Sprache anwenden
        HighlightLanguageButton(language);
    }

    private void btnEnglish_Click(object sender, RoutedEventArgs e)
    {
        var language = "en";
        HighlightLanguageButton(language);
    }

    // == DE: Hover-Effekt für Flags | EN: Hover-Effect for Flags ==
    private void Button_MouseEnter(object sender, MouseEventArgs e)
    {
        if (sender is Button button)
        {
            button.ApplyTemplate();
            string imageName = button.Name.Substring(3) + "Flag";
            var image = button.Template.FindName(imageName, button) as Image;
            if (image != null && image.Tag is string originalUri)
            {
                // Absoluten Pfad zusammensetzen
                string fullPath = Path.Combine(FolderPath, originalUri);
                if (File.Exists(fullPath))
                    image.Source = new BitmapImage(new Uri(fullPath));
                else if (Uri.IsWellFormedUriString(originalUri, UriKind.Absolute))
                    image.Source = new BitmapImage(new Uri(originalUri));
                else
                    image.Source = null; // oder Fallback-Bild setzen
            }

            var textBlock = FindLanguageTextBlock(button);
            if (textBlock != null)
                textBlock.Foreground = Brushes.White;
        }
    }

    private void Button_MouseLeave(object sender, MouseEventArgs e)
    {
        if (sender is Button button)
        {
            if (button == _activeLanguageButton)
                return;
            button.ApplyTemplate();
            string imageName = button.Name.Substring(3) + "Flag";
            var image = button.Template.FindName(imageName, button) as Image;
            if (image != null && image.Tag is string originalUri)
            {
                string fullPath = Path.Combine(FolderPath, originalUri);
                if (File.Exists(fullPath))
                    image.Source = LoadImageAsGrayscale(fullPath);
                else if (Uri.IsWellFormedUriString(originalUri, UriKind.Absolute))
                    image.Source = LoadImageAsGrayscale(originalUri);
                else
                    image.Source = null; // oder Fallback-Graustufenbild
            }

            var textBlock = FindLanguageTextBlock(button);
            if (textBlock != null)
                textBlock.Foreground = Brushes.Gray;
        }
    }
    ///
    /// ||======================================== End ========================================||
    ///     
    
    private void Window_Loaded(object sender, RoutedEventArgs e)
    {
        LoadingIcons();
    }

    ///
    /// ||=========================================||
    /// || ====== DE: Fenster-Drag-Funktion ====== ||
    /// || ====== EN: Window Drag Function  ====== ||
    /// ||=========================================||
    /// 
    private void Window_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {

        if (e.Handled)
            return;
        if ((_activePopup == null || !_activePopup.IsOpen) && e.LeftButton == MouseButtonState.Pressed)
        {
            // Window holen, in dem die Grid enthalten ist
            Window window = Window.GetWindow((DependencyObject)sender);
            window?.DragMove();
        }
    }


    private void Window_PreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        if (_activePopup != null && _activePopup.IsOpen)
        {
            if (IsMouseOverPopup(_activePopup))
            {
                // Klick im aktiven Popup → Event unterdrücken, Fenster darf sich nicht bewegen
                e.Handled = true;
            }
        }
    }

    [System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
    public struct Win32Point
    {
        public int X;
        public int Y;
    }

    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool GetCursorPos(out Win32Point lpPoint);

    private bool IsMouseOverPopup(Popup popup)
    {
        if (popup.Child is not FrameworkElement popupContent)
            return false;

        GetCursorPos(out Win32Point cursorPos);

        Point popupScreenTopLeft = popupContent.PointToScreen(new Point(0, 0));
        double left = popupScreenTopLeft.X;
        double top = popupScreenTopLeft.Y;
        double right = left + popupContent.ActualWidth;
        double bottom = top + popupContent.ActualHeight;

        return cursorPos.X >= left && cursorPos.X <= right &&
            cursorPos.Y >= top && cursorPos.Y <= bottom;
    }

    private void PopupHeaderDragArea_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        e.Handled = true;
    }



    private void BtnMinimize_Click(object sender, RoutedEventArgs e)
    {
        Window w = GetWindowFromSender(sender);
        w.WindowState = WindowState.Minimized;
    }

    ///
    /// ||=============================================================================================================================||
    /// || ====== DE: Beim Schließen des Fensters wird geprüft ob Änderungen vorgenommen wurden ohne zu speichern.              ====== ||
    /// || ======     Wenn Ja wird ein Popup angezeigt das die Änderungen anzeigt und abfragt ob sie gespeichert werden sollen. ====== ||
    /// || ====== EN: When closing the window, check if changes were made without saving.                                       ====== ||
    /// || ======     If yes, a popup will appear that shows the changes and asks if they should be saved.                      ====== || 
    /// || ========================================================== Start ========================================================== ||                          
    /// 

    private string originalMessagesJson = "";
    /// Close Settings Menu and check if something is not saved , when show popup
    private void BtnClose_Click(object sender, RoutedEventArgs e)
    {
        Window w = GetWindowFromSender(sender);
        var SavePopup = (Popup)w.FindName("SavePopup");
        string currentSettingsJson = GetCurrentSettingsJson(w);
        string currentMessagesJson = GetCurrentMessages(w); // Deine Methode, die das aktuelle Nachrichten-JSON zurückgibt
        //MessageBox.Show(LanguagePath, "Path", MessageBoxButton.OK, MessageBoxImage.Information);
        if (File.Exists(LanguagePath))
        {
            languageDict = LoadLanguageSubset(LanguagePath);
            string json = File.ReadAllText(LanguagePath);
            var jObj = JObject.Parse(json);
            // Neues JObject nur mit den drei Keys bauen
            var chatObj = jObj["Chat"];
            var subset = new JObject
            {
                ["failedMessage"] = chatObj["failedMessage"],
                ["updatedMessage"] = chatObj["updatedMessage"],
                ["notInLocalDB"] = chatObj["notInLocalDB"],
            };
            originalMessagesJson = JsonConvert.SerializeObject(subset, Formatting.Indented); // JSON-String mit nur den 3 Keys
        }
        else
        {
        // Datei existiert nicht
        }

        //MessageBox.Show(originalSettingsJson, "Unterschiede", MessageBoxButton.OK, MessageBoxImage.Information);
        //MessageBox.Show(currentSettingsJson, "Unterschiede", MessageBoxButton.OK, MessageBoxImage.Information);
        if (currentSettingsJson != originalSettingsJson || currentMessagesJson != originalMessagesJson)
        {
            // JSON-Validierung
            try
            {
                JObject.Parse(originalSettingsJson);
            }
            catch (JsonReaderException ex)
            {
                MessageBox.Show("Fehler beim Parsen von *originalSettings*:\n" + ex.Message + "\n\n" + originalMessagesJson, "JSON-Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            try
            {
                JObject.Parse(originalMessagesJson);
            }
            catch (JsonReaderException ex)
            {
                MessageBox.Show("Fehler beim Parsen von *originalMessagesjson*:\n" + ex.Message + "\n\n" + originalMessagesJson, "JSON-Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            var alldiffs = ShowSettingsDifferences(originalSettingsJson, currentSettingsJson, originalMessagesJson, currentMessagesJson, w);
            if (alldiffs.Count > 0)
            {
                return;
            }
            else
            {
                // Falls doch keine Unterschiede gefunden wurden (absicherung)
                _lastUpdateResult = null;
                _cancelDownload = true;
                w.Close();
                return;
            }
        }
        else
        {
            _lastUpdateResult = null;
            _cancelDownload = true;
            w.Close();

            return;
        }
    }



    /// Get Current Settings and show what settings were changed and needed to be saved or disposed
    private List<string> ShowSettingsDifferences(string originalSettingsJson, string currentSettingsJson, string originalMessagesJson, string currentMessagesJson, Window w)
    {
        var allDiffs = new List<string>();
        // Unterschiede Settings
        var originalSettings = JObject.Parse(originalSettingsJson);
        var currentSettings = JObject.Parse(currentSettingsJson);
        var settingsDiffs = new List<string>();
        CompareTokens(originalSettings, currentSettings, "Settings", settingsDiffs, w);
        if (settingsDiffs.Count > 0)
        {
            //allDiffs.Add("Einstellungen:");
            allDiffs.AddRange(settingsDiffs);
        }

        // Unterschiede Messages
        var originalMessages = JObject.Parse(originalMessagesJson);
        var currentMessages = JObject.Parse(currentMessagesJson);
        var messagesDiffs = new List<string>();
        CompareTokens(originalMessages, currentMessages, "Messages", messagesDiffs, w);
        if (messagesDiffs.Count > 0)
        {
            if (allDiffs.Count > 0)
                //	allDiffs.Add(""); // Leerzeile als Trennung
                //allDiffs.Add("Nachrichten:");
                allDiffs.AddRange(messagesDiffs);
        }

        if (allDiffs.Count == 0)
        {
        //MessageBox.Show("Es wurden keine Änderungen festgestellt.");
        }
        else
        {
            //string message = "Folgende Änderungen wurden festgestellt:\n\n" + string.Join("\n", allDiffs);
            ShowDiffPopup(allDiffs, w);
        //MessageBox.Show(message, "Unterschiede", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        return allDiffs;
    }

    private Dictionary<string, string> LoadLanguageSubset(string languagePath)
    {
        var fallback = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            {
                "Added",
                "Hinzugefügt"
            },
            {
                "Deleted",
                "Entfernt"
            },
            {
                "Changed",
                "Geändert"
            }
        };
        if (!File.Exists(languagePath))
            return fallback;
        try
        {
            string json = File.ReadAllText(languagePath);
            var jObj = JObject.Parse(json);
            foreach (var key in fallback.Keys.ToList())
            {
                if (jObj.TryGetValue(key, StringComparison.OrdinalIgnoreCase, out var token) && token != null)
                    fallback[key] = token.ToString() ?? fallback[key];
            }

            return fallback;
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Fehler beim Laden der Sprache: {ex.Message}", "Sprache", MessageBoxButton.OK, MessageBoxImage.Warning);
            return fallback;
        }
    }

    private void CompareTokens(JToken original, JToken current, string path, List<string> diffs, Window w)
    {
        if (original == null && current == null)
            return;
        if (original == null)
        {
            diffs.Add($"{GetUiLabel(path, w)}: {languageDict["Changed"]} -> {current}");
            return;
        }

        if (current == null)
        {
            diffs.Add($"{GetUiLabel(path, w)}: {languageDict["Deleted"]} -> {original}");
            return;
        }

        if (JToken.DeepEquals(original, current))
            return;
        if (original.Type != current.Type)
        {
            diffs.Add($"{GetUiLabel(path, w)}: geändert von {original.Type} zu {current.Type}");
            return;
        }

        switch (original.Type)
        {
            case JTokenType.Object:
                var originalObj = (JObject)original;
                var currentObj = (JObject)current;
                var allKeys = new HashSet<string>(originalObj.Properties().Select(p => p.Name));
                allKeys.UnionWith(currentObj.Properties().Select(p => p.Name));
                foreach (var key in allKeys)
                {
                    var origVal = originalObj[key];
                    var currVal = currentObj[key];
                    string newPath = string.IsNullOrEmpty(path) ? key : $"{path}.{key}";
                    CompareTokens(origVal, currVal, newPath, diffs, w);
                }

                break;
            case JTokenType.Array:
                var originalArray = original as JArray;
                var currentArray = current as JArray;
                var originalItems = originalArray.Select(i => i.ToString()).ToList();
                var currentItems = currentArray.Select(i => i.ToString()).ToList();
                var removed = originalItems.Except(currentItems).ToList();
                var added = currentItems.Except(originalItems).ToList();
                foreach (var r in removed)
                    diffs.Add($"{GetUiLabel(path, w)}: {languageDict["Deleted"]} {r}");
                foreach (var a in added)
                    diffs.Add($"{GetUiLabel(path, w)}: {languageDict["Added"]} {a}");
                break;
            default:
                diffs.Add($"{GetUiLabel(path, w)}:{languageDict["Changed"]} '{original}' -> '{current}'");
                break;
        }
    }

    private string GetUiLabel(string path, Window window)
    {
        try
        {
            string lastKey = path.Split('.').Last();
            string labelName = ToPascalCase(lastKey) + "Label";
            if (window.FindName(labelName)is TextBlock label)
                return label.Text;
        }
        catch
        {
        // Fehler ignorieren
        }

        return ToPascalCase(path.Split('.').Last());
    }

    private string ToPascalCase(string input)
    {
        var parts = input.Split(new[] { '_', '-' }, StringSplitOptions.RemoveEmptyEntries);
        return string.Concat(parts.Select(p => !string.IsNullOrEmpty(p) ? char.ToUpper(p[0]) + p.Substring(1) : ""));
    }

    public void ShowDiffPopup(List<string> diffs, Window window)
    {
        var ItemsToSaveStackPanel = (StackPanel)window.FindName("ItemsToSave");
        var SavePopup = (Popup)window.FindName("SavePopup");
        if (languageDict != null && languageDict.Count > 0)
        {
            var text = string.Join(Environment.NewLine, languageDict.Select(kvp => $"{kvp.Key}: {kvp.Value}"));
        //MessageBox.Show(text, "Inhalt von languageDict", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        else
        {
            MessageBox.Show("languageDict ist leer oder null", "Info", MessageBoxButton.OK, MessageBoxImage.Warning);
        }

        ItemsToSaveStackPanel.Children.Clear();
        var groups = diffs.GroupBy(diff =>
        {
            var parts = diff.Split(':');
            return parts.Length > 1 ? parts[0] : "Allgemein";
        });
        foreach (var group in groups)
        {
            var header = new TextBlock
            {
                Text = group.Key,
                FontSize = 16,
                FontWeight = FontWeights.Bold,
                Foreground = Brushes.White,
                Margin = new Thickness(0, 10, 0, 2)
            };
            ItemsToSaveStackPanel.Children.Add(header);
            var subgroup = group.GroupBy(g =>
            {
                var parts = g.Split(':');
                if (parts.Length < 2)
                    return "Andere";
                var rest = parts[1].Trim().Split(' ')[0].ToLowerInvariant();
                return rest switch
                {
                    "hinzugefügt" or "added" => "Added",
                    "entfernt" or "deleted" or "removed" => "Removed",
                    "geändert" or "changed" => "Changed",
                    _ => "Andere"
                };
            });
            foreach (var typeGroup in subgroup)
            {
                string typeKey = typeGroup.Key;
                string typeLabel = languageDict.ContainsKey(typeKey) ? languageDict[typeKey] : typeKey;
                var subheader = new TextBlock
                {
                    Text = typeLabel,
                    FontSize = 14,
                    FontWeight = FontWeights.SemiBold,
                    Foreground = Brushes.LightGray,
                    Margin = new Thickness(20, 5, 0, 2)
                };
                ItemsToSaveStackPanel.Children.Add(subheader);
                foreach (var item in typeGroup)
                {
                    var firstColon = item.IndexOf(':');
                    string text = firstColon >= 0 ? item.Substring(firstColon + 1).Trim() : item;
                    // Schlüsselwörter, die entfernt werden sollen (auf Deutsch und Englisch)
                    string[] keywordsToRemove = new[]
                    {
                        "hinzugefügt",
                        "added",
                        "entfernt",
                        "deleted",
                        "geändert",
                        "changed",
                        "removed"
                    };
                    foreach (var keyword in keywordsToRemove)
                    {
                        // Klein schreiben zum besseren Finden (case insensitive)
                        int index = text.ToLowerInvariant().IndexOf(keyword);
                        if (index >= 0)
                        {
                            // Entferne das Schlüsselwort + optional ein führendes Leerzeichen
                            text = text.Remove(index, keyword.Length).TrimStart();
                            break; // nur einmal entfernen, wenn du mehrere hast
                        }
                    }

                    var bulletItem = new TextBlock
                    {
                        Text = "• " + text,
                        FontSize = 12,
                        Margin = new Thickness(40, 2, 20, 0),
                        Foreground = Brushes.White,
                        TextWrapping = TextWrapping.Wrap,
                        MaxWidth = 700
                    };
                    ItemsToSaveStackPanel.Children.Add(bulletItem);
                }
            }
        }

        if (SavePopup != null)
        {
            SavePopup.IsOpen = true; // Popup öffnen
            //LoadingIcons();
            LoadPopupIcons(SavePopup);
        }
        else
        {
            MessageBox.Show("Popup not found.");
        }
    //SavePopup.IsOpen = true;
    //MessageBox.Show("Savepopup!");
    }
    private string GetCurrentSettingsJson(Window window)
    {
        // Schritt 1: Aktuelle Settings aus UI einlesen (wie gehabt)
        var currentSettings = new Dictionary<string, JToken>(StringComparer.OrdinalIgnoreCase)
        {
            ["twitch"] = new JObject
            {
                ["CLIENT_ID"] = ((PasswordBox)window.FindName("ClientIDHideBox")).Password,
                ["OAuth_token"] = ((PasswordBox)window.FindName("TokenHideBox")).Password
            },
            ["paths"] = new JObject
            {
                ["allowed_paths"] = new JArray(((ListBox)window.FindName("Allowed_Paths")).Items.Cast<ListBoxItem>().Select(i => i.Content.ToString())),
                ["excluded_names"] = new JArray(((ListBox)window.FindName("Excluded_Names")).Items.Cast<ListBoxItem>().Select(i => i.Content.ToString())),
                ["excluded_folders"] = new JArray(((ListBox)window.FindName("Excluded_Folders")).Items.Cast<ListBoxItem>().Select(i => i.Content.ToString()))
            },
            ["streamerbot"] = new JObject
            {
                ["url"] = ((TextBox)window.FindName("StreamerBotUrl")).Text,
                ["port"] = ((TextBox)window.FindName("StreamerBotPort")).Text
            },
            ["options"] = new JObject
            {
                ["Box_Art_Size"] = GetCurrentBoxArtSizeString(window),
                ["similarity"] = (int)((Slider)window.FindName("sldSimilarity")).Value,
                ["watch_streamerbot"] = ((ToggleButton)window.FindName("toggleWatchStreamerBot")).IsChecked == true,
                ["watch_obs"] = ((ToggleButton)window.FindName("toggleWatchOBS")).IsChecked == true,
                ["only_local_db"] = ((ToggleButton)window.FindName("toggleOnlyLocalDb")).IsChecked == true,
                ["show_console"] = ((ToggleButton)window.FindName("toggleShowConsole")).IsChecked == true,
                ["message"] = ((ToggleButton)window.FindName("toggleMessageEnabled")).IsChecked == true,
                ["censor_mode"] = ((ToggleButton)window.FindName("toggleCensorMode")).IsChecked == true,
                ["AsAnnouncement"] = ((ToggleButton)window.FindName("toggleAsAnnouncement")).IsChecked == true,
                ["kick_enabled"] = ((ToggleButton)window.FindName("toggleKick")).IsChecked == true,
                ["playnite_enabled"] = ((ToggleButton)window.FindName("togglePlaynite")).IsChecked == true,
                ["language"] = currentLanguage,
                ["delay_general"] = (int)((Slider)window.FindName("sldDelayGeneral")).Value,
                ["delay_programming"] = (int)((Slider)window.FindName("sldDelayProgramming")).Value,
                ["delay_playnite"] = (int)((Slider)window.FindName("sldDelayPlaynite")).Value
            }
        };

        // Neues JObject aus aktuellem Dictionary
        var currentJObject = JObject.FromObject(currentSettings);

        // Schritt 2: Original JSON parsen
        if (originalSettingsJson != null)
        {
            var originalJObject = JObject.Parse(originalSettingsJson);

            // Schritt 3: DeepMerge original in current (Originalwerte nur ergänzen, nicht überschreiben)
            DeepMerge(originalJObject, currentJObject);

            // Schritt 4: Rekursiv in Originalreihenfolge aufbauen
            var orderedResult = PreserveOrder(originalJObject, currentJObject);

            // Schritt 5: Stringify und zurückgeben
            return orderedResult.ToString(Formatting.Indented);
        }

        // Kein Original vorhanden -> einfach currentJObject in Standard-Reihenfolge zurückgeben
        return currentJObject.ToString(Formatting.Indented);
    }


    private JObject PreserveOrder(JObject original, JObject current)
    {
        var ordered = new JObject();

        // Erst die Keys aus dem Original, in Originalreihenfolge
        foreach (var prop in original.Properties())
        {
            if (current.TryGetValue(prop.Name, out var currentVal))
            {
                // Wenn beides ein Objekt -> rekursiv
                if (prop.Value.Type == JTokenType.Object && currentVal.Type == JTokenType.Object)
                {
                    ordered[prop.Name] = PreserveOrder((JObject)prop.Value, (JObject)currentVal);
                }
                else
                {
                    ordered[prop.Name] = currentVal;
                }
            }
            else
            {
                // Falls im aktuellen fehlt → Original übernehmen
                ordered[prop.Name] = prop.Value.DeepClone();
            }
        }

        // Danach Keys aus current, die im Original nicht existierten
        foreach (var prop in current.Properties())
        {
            if (!ordered.ContainsKey(prop.Name))
            {
                ordered[prop.Name] = prop.Value;
            }
        }

        return ordered;
    }


    private string GetCurrentMessages(Window window)
    {
        var messages = new
        {
            updatedMessage = ((TextBox)window.FindName("txtUpdateMessage"))?.Text ?? "",
            failedMessage = ((TextBox)window.FindName("txtFailedMessage"))?.Text ?? "",
            notInLocalDB = ((TextBox)window.FindName("txtNotInLocalDBMessage"))?.Text ?? "",
        };
        string currentMessages = JsonConvert.SerializeObject(messages, Formatting.Indented);
        return currentMessages;
    }

    private void DeepMerge(JObject original, JObject current)
    {
        foreach (var property in original.Properties())
        {
            if (!current.ContainsKey(property.Name))
            {
                current[property.Name] = property.Value.DeepClone();
            }
            else
            {
                if (property.Value.Type == JTokenType.Object && current[property.Name].Type == JTokenType.Object)
                {
                    DeepMerge((JObject)property.Value, (JObject)current[property.Name]);
                }
                else if (property.Value.Type == JTokenType.Array && current[property.Name].Type != JTokenType.Array)
                {
                    current[property.Name] = property.Value.DeepClone();
                }
            }
        }
    }

    /// Save settings in save popup and direct per save button
    private void btnConfirmSave_Click(object sender, RoutedEventArgs e)
    {
        Window w = GetWindowFromSender(sender);
        var SavePopup = (Popup)w.FindName("SavePopup");
        SavePopup.IsOpen = false;
        // Aktuelle JSONs aus dem UI abrufen
        string currentSettingsJson = GetCurrentSettingsJson(w);
        string currentMessagesJson = GetCurrentMessages(w);
        try
        {
            File.WriteAllText(configPath, currentSettingsJson, new System.Text.UTF8Encoding(false));
            //originalSettingsJson = updatedSettingsJson;
            MessageBox.Show(
                currentLanguage == "de" ? "Einstellungen erfolgreich gespeichert." : "Settings saved successfully.",
                currentLanguage == "de" ? "Erfolg" : "Success",
                MessageBoxButton.OK,
                MessageBoxImage.Information
            );

        }
        catch (Exception ex)
        {
            MessageBox.Show(
                currentLanguage == "de" ? $"Fehler beim Speichern: {ex.Message}" : $"Error while saving: {ex.Message}",
                currentLanguage == "de" ? "Fehler" : "Error",
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );

        }

        // Fenster schließen, wenn gewünscht
        _lastUpdateResult = null;
        _cancelDownload = true;
        
        w.Close();
    }


    private void btnAbortSave_Click(object sender, RoutedEventArgs e)
    {
        Window w = GetWindowFromSender(sender);
        var SavePopup = (Popup)w.FindName("SavePopup");
        SavePopup.IsOpen = false;
        w.Close();
    }

    ///
    /// || =========================================================== End =========================================================== ||
    /// 
    /// ||===========================================================||
    /// || ====== DE: About Button zum öffnen der About Seite ====== ||
    /// || ======   EN: About Button to open About Overlay    ====== || 
    /// ||===========================================================||
    /// 
    private void BtnAbout_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);

        var AboutOverlay = (Grid)window.FindName("AboutOverlay");
        var SettingsOverlay = (Grid)window.FindName("SettingsOverlay");
        ((Run)window.FindName("Settingmenu_Version")).Text = "v" + _localVersion.SettingsVersion;
        ((Run)window.FindName("Program_Version")).Text = "v" + _localVersion.ProgramVersion; 

        HideOverlay(SettingsOverlay, SlideDirection.Right);

        // DE: DispatcherTimer für Pause | EN: DispatcherTimer for pause 
        var timer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(150) // gleiche Dauer wie SlideDurationMs
        };
        timer.Tick += (s, e) =>
        {
            timer.Stop();
            // Slide nach rechts raus
            ShowOverlay(AboutOverlay, SlideDirection.Left);
        };
        timer.Start();
        // Slide von links rein

        // Slide von oben rein
        //ShowOverlay(UpdateOverlay, SlideDirection.Top);

        // Slide nach unten raus
        //HideOverlay(UpdateOverlay, SlideDirection.Bottom);

        CheckAutoUpdate();
        LoadingIcons();
    }

    ///
    /// ||=================================================================================||
    /// || ====== DE: Back Button zum zurückkehren zur About oder Einstellungsseite ====== ||
    /// || ======    EN: Back Button to return to the About or Settings Overlay     ====== ||
    /// ||=================================================================================||
    /// 
    private void BtnBack_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var AboutOverlay = (Grid)window.FindName("AboutOverlay");
        var SettingsOverlay = (Grid)window.FindName("SettingsOverlay");
        var UpdateOverlay = (Grid)window.FindName("UpdateOverlay");
        if (AboutOverlay.Visibility == Visibility.Visible)
        {
            // Slide von links rein
            HideOverlay(AboutOverlay, SlideDirection.Left);
            // DispatcherTimer für Pause
            var timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(150) // gleiche Dauer wie SlideDurationMs
            };
            timer.Tick += (s, e) =>
            {
                timer.Stop();
                // Slide nach rechts raus
                ShowOverlay(SettingsOverlay, SlideDirection.Right);
            };
            timer.Start();
            // Slide nach rechts raus
            //HideOverlay(AboutOverlay, SlideDirection.Left);            
            //SettingsOverlay.Visibility = Visibility.Visible;
            //AboutOverlay.Visibility = Visibility.Collapsed;
        }

        if (UpdateOverlay.Visibility == Visibility.Visible)
        {
            UpdateOverlay.Visibility = Visibility.Collapsed;
            AboutOverlay.Visibility = Visibility.Visible;
            ResetUpdateOverlay();
        }
        CheckAutoUpdate();
    }

    ///
    /// ||========================================================||
    /// || ====== DE: Discord Button zum öffnen von Discord ======||
    /// || ======    EN: Discord Button to open Discord     ======||
    /// ||========================================================||
    /// 
    private void BtnDiscord_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            // Discord per Standardprotokoll öffnen (z. B. Einladung, Kanal etc.)
            string discordUrl = "https://discord.com/channels/834650675224248362/1337058491608862761"; // oder z. B. dein Server-Invite-Link

            var psi = new System.Diagnostics.ProcessStartInfo
            {
                FileName = discordUrl,
                UseShellExecute = true // wichtig, damit Standardbrowser geöffnet wird
            };
            System.Diagnostics.Process.Start(psi);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Konnte Discord nicht öffnen: {ex.Message}", "Fehler", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

     
    /// Twitch Oauth Token and Client ID functions to mask them, more or less used from mustached's original code
    private void ClientIDHideBox_PasswordChanged(object sender, RoutedEventArgs e)
    {
        PasswordBox pb = (PasswordBox)sender;
        var window = GetWindowFromSender(sender);
        ((TextBlock)window.FindName("ClientIDPlaceholder")).Visibility = string.IsNullOrEmpty(pb.Password) ? Visibility.Visible : Visibility.Collapsed;
    }



    private async void ClientIDToggle_Click(object sender, RoutedEventArgs e)
    {
        var toggle = (ToggleButton)sender;
        var window = GetWindowFromSender(sender);
        var ClientIDHideBox = (PasswordBox)window.FindName("ClientIDHideBox");
        var ClientIDShowBox = (TextBox)window.FindName("ClientIDShowBox");
        if (toggle.IsChecked == true)
        {
            ClientIDShowBox.Text = ClientIDHideBox.Password;
            ClientIDShowBox.Visibility = Visibility.Visible;
            ClientIDHideBox.Visibility = Visibility.Collapsed;
        }
        else
        {
            ClientIDHideBox.Password = ClientIDShowBox.Text;
            ClientIDHideBox.Visibility = Visibility.Visible;
            ClientIDShowBox.Visibility = Visibility.Collapsed;
        }

        // Tag aus XAML lesen
        string tagPath = toggle.Tag as string;
        if (string.IsNullOrWhiteSpace(tagPath))
            return;

        string targetPath = Path.Combine(FolderPath, tagPath.Replace("/", "\\"));

        // URL anhand des Tags bestimmen
        string downloadUrl = null;
        switch (Path.GetFileName(tagPath).ToLower())
        {
            case "hidden.png":
                downloadUrl = "https://img.icons8.com/?size=100&id=uIlosonmVLUK&format=png&color=A9A9A9";
                break;
            case "visible.png":
                downloadUrl = "https://img.icons8.com/?size=100&id=60022&format=png&color=A9A9A9";
                break;
        }

        try
        {
            // Falls Datei fehlt → downloaden
            if (!File.Exists(targetPath) && !string.IsNullOrWhiteSpace(downloadUrl))
            {
                string dir = Path.GetDirectoryName(targetPath);
                if (!Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                using (var client = new System.Net.Http.HttpClient())
                {
                    byte[] imageBytes = await client.GetByteArrayAsync(downloadUrl);
                    File.WriteAllBytes(targetPath, imageBytes);
                }
            }

            // Icon setzen
            var bmp = new BitmapImage(new Uri(targetPath, UriKind.Absolute));
            toggle.Background = new ImageBrush(bmp) { Stretch = Stretch.Uniform };
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Fehler beim Laden/Setzen des Icons:\n{ex.Message}", "Fehler");
        }
    }

    private void TokenHideBox_PasswordChanged(object sender, RoutedEventArgs e)
    {
        PasswordBox pb = (PasswordBox)sender;
        var window = GetWindowFromSender(sender);
        ((TextBlock)window.FindName("TokenPlaceholder")).Visibility = string.IsNullOrEmpty(pb.Password) ? Visibility.Visible : Visibility.Collapsed;
    }


    private async void TokenToggle_Click(object sender, RoutedEventArgs e)
    {
        var toggle = (ToggleButton)sender;
        var window = GetWindowFromSender(sender);
        var TokenHideBox = (PasswordBox)window.FindName("TokenHideBox");
        var TokenShowBox = (TextBox)window.FindName("TokenShowBox");
        // Umschalten zwischen Passwort / Text
        if (toggle.IsChecked == true)
        {
            TokenShowBox.Text = TokenHideBox.Password;
            TokenShowBox.Visibility = Visibility.Visible;
            TokenHideBox.Visibility = Visibility.Collapsed;
        }
        else
        {
            TokenHideBox.Password = TokenShowBox.Text;
            TokenHideBox.Visibility = Visibility.Visible;
            TokenShowBox.Visibility = Visibility.Collapsed;
        }
        // Tag aus XAML lesen
        string tagPath = toggle.Tag as string;
        if (string.IsNullOrWhiteSpace(tagPath))
            return;

        string targetPath = Path.Combine(FolderPath, tagPath.Replace("/", "\\"));

        // URL anhand des Tags bestimmen
        string downloadUrl = null;
        switch (Path.GetFileName(tagPath).ToLower())
        {
            case "hidden.png":
                downloadUrl = "https://img.icons8.com/?size=100&id=uIlosonmVLUK&format=png&color=A9A9A9";
                break;
            case "visible.png":
                downloadUrl = "https://img.icons8.com/?size=100&id=60022&format=png&color=A9A9A9";
                break;
        }

        try
        {
            if (!File.Exists(targetPath) && !string.IsNullOrWhiteSpace(downloadUrl))
            {
                string dir = Path.GetDirectoryName(targetPath);
                if (!Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                using (var client = new System.Net.Http.HttpClient())
                {
                    byte[] imageBytes = await client.GetByteArrayAsync(downloadUrl);
                    File.WriteAllBytes(targetPath, imageBytes);
                }
            }

            // Icon setzen
            var bmp = new BitmapImage(new Uri(targetPath, UriKind.Absolute));
            toggle.Background = new ImageBrush(bmp) { Stretch = Stretch.Uniform };
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Fehler beim Laden/Setzen des Icons:\n{ex.Message}", "Fehler");
        }
            
    }
     
    ///
    /// ||=================================================||
    /// || ====== DE: Box Art Size Slider Funktionen ======||
    /// || ======  EN: Box Art Size Slider Functions ======||
    /// ||===================== Start =====================||
    /// 
    private string GetCurrentBoxArtSizeString(Window window)
    {
        var sldBoxSize = (Slider)window.FindName("sldBoxSize");
        int index = (int)sldBoxSize.Value;
        if (index >= 0 && index < BoxSizeHelper.StandardSizes.Count)
        {
            var size = BoxSizeHelper.StandardSizes[index];
            return $"{(int)size.Width}x{(int)size.Height}";
        }

        return "285x380";
    }

    public static class BoxSizeHelper
    {
        public static readonly List<Size> StandardSizes = new()
        {
            new Size(240, 320),
            new Size(285, 380),
            new Size(300, 400),
            new Size(360, 480),
            new Size(480, 640),
            new Size(600, 800),
            new Size(720, 960),
            new Size(768, 1024),
            new Size(1080, 1440)
        };
        public static Size SnapToStandardBoxArtSize(double width, double height)
        {
            foreach (var size in StandardSizes)
            {
                if (size.Width == width && size.Height == height)
                    return size;
            }

            foreach (var size in StandardSizes)
            {
                if (size.Width >= width && size.Height >= height)
                    return size;
            }

            double newWidth = Math.Ceiling(width / 3.0) * 3;
            double newHeight = Math.Ceiling(newWidth * 4.0 / 3.0);
            return new Size(newWidth, newHeight);
        }

        public static int GetIndexOfSize(Size size)
        {
            for (int i = 0; i < StandardSizes.Count; i++)
            {
                if (StandardSizes[i].Width == size.Width && StandardSizes[i].Height == size.Height)
                    return i;
            }

            return -1;
        }

        public static Size ParseSize(string sizeString)
        {
            var parts = sizeString.Split('x');
            if (parts.Length == 2 && double.TryParse(parts[0], out double w) && double.TryParse(parts[1], out double h))
            {
                return new Size(w, h);
            }

            return new Size(285, 380); // Default
        }
    }

    private void sldBoxSize_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
    {
        var window = Application.Current.MainWindow; // Oder übergeben, je nach Kontext
        var txtBoxSize = (TextBlock)window.FindName("txtBoxSize");
        var sldBoxSize = (Slider)window.FindName("sldBoxSize");
        int index = (int)e.NewValue;
        UpdateBoxSizeDisplay(index);
    }

    private void UpdateBoxSizeDisplay(int selectedIndex)
    {
        var window = Application.Current.MainWindow;
        var BoxArtSizeValue = (Run)window.FindName("BoxArtSizeValue");
        if (selectedIndex >= 0 && selectedIndex < BoxSizeHelper.StandardSizes.Count)
        {
            var size = BoxSizeHelper.StandardSizes[selectedIndex];
            BoxArtSizeValue.Text = $"{(int)size.Width} x {(int)size.Height}";
        }
    }

    // Hilfsmethode zum Setzen der Placeholder-Sichtbarkeit
    private void UpdatePasswordPlaceholder(PasswordBox box, TextBlock placeholder)
    {
        placeholder.Visibility = string.IsNullOrEmpty(box.Password) ? Visibility.Visible : Visibility.Collapsed;
    }
    ///
    /// ||======================================== End ========================================||
    /// 

    private Window GetWindowFromSender(object sender)
    {
        if (sender is FrameworkElement fe)
            return Window.GetWindow(fe);
        return null;
    }

    // private void ToggleUpdate_Click(object sender, RoutedEventArgs e)
    // {
    //     var window = Window.GetWindow(sender as DependencyObject);
    //     var toggleMessageEnabled = (ToggleButton)window.FindName("toggleMessageEnabled");
    //     var toggleUpdateMessage = (ToggleButton)window.FindName("toggleUpdateMessage");
    //     if (toggleMessageEnabled.IsChecked == true)
    //     {
    //         toggleUpdateMessage.IsEnabled = true;
    //     }
    //     else
    //     {
    //         toggleUpdateMessage.IsChecked = false;
    //     //toggleUpdateMessage.IsEnabled = false;
    //     }
    // }

    private void AddNameButton_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var ExeNamePopup = (Popup)window.FindName("ExeNamePopup");
        if (ExeNamePopup != null)
        {
            ExeNamePopup.IsOpen = true; // Popup öffnen
            //LoadingIcons();
            LoadPopupIcons(ExeNamePopup);
        }
        else
        {
            MessageBox.Show("Add Name Popup not found.");
        }
    }

    private void OnCancelClick(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var ExeNamePopup = (Popup)window.FindName("ExeNamePopup");
        var txtExeName = (TextBox)window.FindName("ExeNameBox");
        var placeholder = (TextBlock)window.FindName("txtExeNamePlaceholder");
        if (ExeNamePopup != null)
        {
            ExeNamePopup.IsOpen = false; // Popup schließen
            txtExeName.Clear();
        }
    }

    private void ExeNameBox_Enter(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter)
        {
            // Enter wurde gedrückt – hier deine Logik aufrufen
            AddExeName_Click(sender, null);
            // Optional verhindern, dass der „Pling“-Sound abgespielt wird
            e.Handled = true;
        }
    }

    private void AddExeName_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var ExeNamePopup = (Popup)window.FindName("ExeNamePopup");
        var txtExeName = (TextBox)window.FindName("ExeNameBox");
        var placeholder = (TextBlock)window.FindName("txtExeNamePlaceholder");
        var Excluded_Names = (ListBox)window.FindName("Excluded_Names");
        string ExeName = txtExeName?.Text?.Trim();
        if (!string.IsNullOrEmpty(ExeName))
        {
            // Prüfen, ob ".exe" vorhanden ist
            if (!ExeName.EndsWith(".exe", StringComparison.OrdinalIgnoreCase))
                ExeName += ".exe";
            // Prüfen, ob der Name schon enthalten ist
            var existingItem = Excluded_Names.Items.OfType<ListBoxItem>().FirstOrDefault(item => item.Content?.ToString().Equals(ExeName, StringComparison.OrdinalIgnoreCase) == true);
            if (existingItem == null)
            {
                // Neues Item hinzufügen
                var newItem = new ListBoxItem
                {
                    Content = ExeName
                };
                Excluded_Names.Items.Add(newItem);
                Excluded_Names.UpdateLayout(); // notwendig vor ScrollIntoView
                Excluded_Names.ScrollIntoView(newItem);
                // Highlight: Hellgrün -> Transparent
                var highlightBrush = new SolidColorBrush(Colors.LightGreen);
                newItem.Background = highlightBrush;
                var animation = new ColorAnimation
                {
                    To = Colors.Transparent,
                    Duration = TimeSpan.FromMilliseconds(800),
                    BeginTime = TimeSpan.FromMilliseconds(300),
                    EasingFunction = new QuadraticEase
                    {
                        EasingMode = EasingMode.EaseOut
                    }
                };
                highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
            //MessageBox.Show($"New Name Added: {ExeName}");
            }
            else
            {
                // Bereits vorhandenes Item hervorheben: IndianRed -> Original
                Excluded_Names.UpdateLayout();
                Excluded_Names.ScrollIntoView(existingItem);
                var originalBrush = existingItem.Background as SolidColorBrush;
                if (originalBrush == null || originalBrush.IsFrozen)
                    originalBrush = new SolidColorBrush(Colors.Transparent);
                var highlightBrush = new SolidColorBrush(Colors.IndianRed);
                existingItem.Background = highlightBrush;
                var animation = new ColorAnimation
                {
                    To = originalBrush.Color,
                    Duration = TimeSpan.FromMilliseconds(600),
                    BeginTime = TimeSpan.FromMilliseconds(300),
                    EasingFunction = new QuadraticEase
                    {
                        EasingMode = EasingMode.EaseInOut
                    }
                };
                highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
            }

            // Textbox leeren, Platzhalter anzeigen, Popup schließen
            txtExeName.Clear();
            placeholder.Visibility = Visibility.Visible;
            ExeNamePopup.IsOpen = false;
        }
        else
        {
            MessageBox.Show("Please enter a name.");
        }
    }

    private void ExeNameBox_TextChanged(object sender, TextChangedEventArgs e)
    {
        var window = Window.GetWindow((DependencyObject)sender);
        var textBox = (TextBox)sender;
        var placeholder = (TextBlock)window.FindName("txtExeNamePlaceholder");
        placeholder.Visibility = string.IsNullOrWhiteSpace(textBox.Text) ? Visibility.Visible : Visibility.Collapsed;
    }

    private void Toggle_Unchecked(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var toggle = sender as ToggleButton;

        if (toggle?.Name == "toggleAllowedPaths")
        {
            var Allowed_Paths = (ListBox)window.FindName("Allowed_Paths");
            Allowed_Paths.SelectedItems.Clear();
        }
        else if (toggle?.Name == "toggleNames")
        {
            var Excluded_Names = (ListBox)window.FindName("Excluded_Names");
            Excluded_Names.SelectedItems.Clear();
        }
        else if (toggle?.Name == "toggleExcludedFolders")
        {
            var Excluded_Folders = (ListBox)window.FindName("Excluded_Folders");
            Excluded_Folders.SelectedItems.Clear();
        }
    }

    ///
    /// ||===================================================================================||
    /// || ====== DE: Löschfunktion für alle Listboxen die ausgewählte Einträge löscht ======||
    /// || ======  EN: Delete function for all listboxes that deletes selected entries ======||
    /// ||===================================================================================||
    /// 
    private void Delete_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var button = sender as Button;
        Popup delPopup = null;
        ListBox excludedList = null;
        ItemsControl namesToDelete = null;
        // Entscheide je nach Button-Name, welche UI-Elemente verwendet werden
        if (button?.Name == "btnDelete")
        {
            delPopup = (Popup)window.FindName("DeletePopup");
            excludedList = (ListBox)window.FindName("Excluded_Names");
            namesToDelete = (ItemsControl)window.FindName("NamesToDelete");
        }
        else if (button?.Name == "btnDelExcludedFolders")
        {
            delPopup = (Popup)window.FindName("DeletePopup");
            excludedList = (ListBox)window.FindName("Excluded_Folders");
            namesToDelete = (ItemsControl)window.FindName("NamesToDelete");
        }
        else if (button?.Name == "btnDelAllowedPath")
        {
            delPopup = (Popup)window.FindName("DeletePopup");
            excludedList = (ListBox)window.FindName("Allowed_Paths");
            namesToDelete = (ItemsControl)window.FindName("NamesToDelete");
        }

        if (excludedList == null || delPopup == null || namesToDelete == null)
        {
            MessageBox.Show("UI elements not found.");
            return;
        }

        var selectedItems = excludedList.SelectedItems.Cast<object>().ToList();
        var selected = excludedList.SelectedItems.Cast<ListBoxItem>().ToList();
        if (selected.Count == 0)
            return;
        var orderedSelection = excludedList.Items.Cast<ListBoxItem>().Where(item => selectedItems.Contains(item)).Select(item => item.Content.ToString()).ToList();
        namesToDelete.ItemsSource = orderedSelection;
        delPopup.Tag = button?.Name;
        delPopup.IsOpen = true;
        LoadPopupIcons(delPopup);
    }


    private void btnConfirmDelete_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var delPopup = (Popup)window.FindName("DeletePopup");
        if (delPopup == null)
            return;
        var opener = delPopup.Tag as string;
        ListBox excludedList = null;
        if (opener == "btnDelete")
            excludedList = (ListBox)window.FindName("Excluded_Names");
        else if (opener == "btnDelExcludedFolders")
            excludedList = (ListBox)window.FindName("Excluded_Folders");
        else if (opener == "btnDelAllowedPath")
            excludedList = (ListBox)window.FindName("Allowed_Paths");
        if (excludedList == null)
            return;
        var itemsToDelete = excludedList.SelectedItems.Cast<ListBoxItem>().ToList();
        foreach (var item in itemsToDelete)
        {
            var fadeOut = new DoubleAnimation
            {
                To = 0,
                Duration = TimeSpan.FromMilliseconds(300),
                EasingFunction = new QuadraticEase
                {
                    EasingMode = EasingMode.EaseInOut
                }
            };
            fadeOut.Completed += (s, _) => excludedList.Items.Remove(item);
            item.BeginAnimation(UIElement.OpacityProperty, fadeOut);
        }

        delPopup.IsOpen = false;
    }

    private void btnAbortDelete_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var button = sender as Button;
        Popup delPopup = null;
        if (button?.Name == "btnAbortDelete")
            delPopup = (Popup)window.FindName("DeletePopup");
        else if (button?.Name == "btnAbortDelete")
            delPopup = (Popup)window.FindName("DeletePopup");
        if (delPopup != null)
            delPopup.IsOpen = false;
    }

    ///
    /// ||===================================================================||
    /// || ====== DE: Laufwerk/Ordne Auswählen Menü für das Hinzufügen ======||
    /// || ======     EN: Drive/Folder Selection Menu for Addition     ======||
    /// ||============================== Start ==============================||
    ///     
    private void LoadDrives(object sender, string context = "Name")
    {
        var window = GetWindowFromSender(sender);
        var driveTreeViewName = context == "Path" ? "DriveTreeViewPath" : "DriveTreeView";
        var folderTreeViewName = context == "Path" ? "FolderTreeViewPath" : "FolderTreeView";
        var DriveTreeView = (TreeView)window.FindName(driveTreeViewName);
        if (DriveTreeView == null)
            return;
        var whiteItemStyle = new Style(typeof(TreeViewItem));
        whiteItemStyle.Setters.Add(new Setter(Control.ForegroundProperty, Brushes.White));
        DriveTreeView.Items.Clear();
        foreach (var drive in DriveInfo.GetDrives())
        {
            if (!drive.IsReady)
                continue;
            string volumeLabel = drive.VolumeLabel;
            string displayName = string.IsNullOrWhiteSpace(volumeLabel) ? drive.Name : $"{drive.Name} ({volumeLabel})";
            var item = new TreeViewItem
            {
                Header = displayName,
                Tag = drive.Name,
                Style = whiteItemStyle
            };
            item.Selected += (s, e) => DriveTreeView_SelectedItemChanged(s, e, context);
            DriveTreeView.Items.Add(item);
        }
    }

    private void Folder_Expanded(object sender, RoutedEventArgs e, string context = "Name")
    {
        if (sender is not TreeViewItem item)
            return;
        if (item.Items.Count == 1 && item.Items[0] == null)
        {
            item.Items.Clear();
            var whiteItemStyle = new Style(typeof(TreeViewItem));
            whiteItemStyle.Setters.Add(new Setter(Control.ForegroundProperty, Brushes.White));
            try
            {
                foreach (var dir in Directory.GetDirectories(item.Tag.ToString()))
                {
                    var subItem = new TreeViewItem
                    {
                        Header = Path.GetFileName(dir),
                        Tag = dir,
                        Style = whiteItemStyle
                    };
                    subItem.Items.Add(null); // Dummy
                    subItem.Expanded += (s, ev) => Folder_Expanded(s, ev, context);
                    item.Items.Add(subItem);
                }
            }
            catch
            {
            }
        }
    }

    private void DriveTreeView_SelectedItemChanged(object sender, RoutedEventArgs e, string context = "Name")
    {
        var window = GetWindowFromSender(sender);
        var folderTreeViewName = context == "Path" ? "FolderTreeViewPath" : "FolderTreeView";
        var FolderTreeView = (TreeView)window.FindName(folderTreeViewName);
        if (sender is not TreeViewItem selectedDriveItem)
            return;
        string selectedDrive = selectedDriveItem.Tag?.ToString();
        if (string.IsNullOrWhiteSpace(selectedDrive) || FolderTreeView == null)
            return;
        FolderTreeView.Items.Clear();
        var whiteItemStyle = new Style(typeof(TreeViewItem));
        whiteItemStyle.Setters.Add(new Setter(Control.ForegroundProperty, Brushes.White));
        try
        {
            foreach (var dir in Directory.GetDirectories(selectedDrive))
            {
                var subItem = new TreeViewItem
                {
                    Header = Path.GetFileName(dir),
                    Tag = dir,
                    Style = whiteItemStyle
                };
                subItem.Items.Add(null); // Dummy
                subItem.Expanded += (s, ev) => Folder_Expanded(s, ev, context);
                FolderTreeView.Items.Add(subItem);
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Fehler beim Laden des Verzeichnisses: {ex.Message}");
        }
    }

    private void FolderTreeView_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e, string context = "Name")
    {
        var window = GetWindowFromSender(sender);
        var folderTreeViewName = context == "Path" ? "FolderTreeViewPath" : "FolderTreeView";
        var FolderTreeView = (TreeView)window.FindName(folderTreeViewName);
        if (FolderTreeView?.SelectedItem is not TreeViewItem selectedItem)
            return;
        string selectedPath = selectedItem.Tag?.ToString();
    }
    ///
    /// ||======================================== End ========================================||
    ///



    private void ScrollViewer_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
    {
        if (sender is ScrollViewer sv)
        {
            // Scroll um 3 Zeilen pro Mausrad "Klick"
            int lines = Math.Abs(e.Delta) / 120;
            for (int i = 0; i < lines; i++)
            {
                if (e.Delta > 0)
                    sv.LineUp();
                else
                    sv.LineDown();
            }

            e.Handled = true;
        }
    }

    private ScrollViewer FindScrollViewer(DependencyObject d)
    {
        if (d is ScrollViewer viewer)
            return viewer;
        for (int i = 0; i < VisualTreeHelper.GetChildrenCount(d); i++)
        {
            var child = VisualTreeHelper.GetChild(d, i);
            var result = FindScrollViewer(child);
            if (result != null)
                return result;
        }

        return null;
    }

    ///
    /// ||=====================================================================================================||
    /// || ====== DE: Button zum Bestätigen der Hinzufügung von Ordnernamen und prüft ob schon vorhanden ======||
    /// || ======     EN: Button to Confirm the Addition of Folder Names and Check if already Exists     ======||
    /// ||=====================================================================================================||
    ///     
    private void btnConfirmAddFolderName_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var folderTreeView = (TreeView)window.FindName("FolderTreeView");
        var driveTreeView = (TreeView)window.FindName("DriveTreeViewPath");
        var Excluded_Folders_Listbox = (ListBox)window.FindName("Excluded_Folders");
        var AddFolderNamePopup = (Popup)window.FindName("AddFolderNamePopup");
        string selectedPath = null;
        if (folderTreeView?.SelectedItem is TreeViewItem folderItem)
            selectedPath = folderItem.Tag?.ToString();
        else if (driveTreeView?.SelectedItem is TreeViewItem driveItem)
            selectedPath = driveItem.Tag?.ToString();
        if (string.IsNullOrWhiteSpace(selectedPath))
            return;
        // Laufwerksbuchstaben ignorieren (z. B. "C:\")
        if (selectedPath.Length == 3 && selectedPath[1] == ':' && selectedPath[2] == '\\' && char.IsLetter(selectedPath[0]))
        {
            return; // Einfach abbrechen, kein Popup anzeigen
        }

        // Nur letzten Ordnernamen extrahieren
        string folderNameOnly = System.IO.Path.GetFileName(selectedPath.TrimEnd('\\'));
        if (string.IsNullOrWhiteSpace(folderNameOnly))
            return;
        // Prüfen ob schon enthalten
        bool alreadyExists = Excluded_Folders_Listbox.Items.OfType<ListBoxItem>().Any(item => item.Content?.ToString().Equals(folderNameOnly, StringComparison.OrdinalIgnoreCase) == true);
        if (!alreadyExists)
        {
            var newItem = new ListBoxItem
            {
                Content = folderNameOnly
            };
            Excluded_Folders_Listbox.Items.Add(newItem);
            Excluded_Folders_Listbox.UpdateLayout(); // notwendig vor ScrollIntoView
            Excluded_Folders_Listbox.ScrollIntoView(newItem);
            // Highlight
            var highlightBrush = new SolidColorBrush(Colors.LightGreen);
            newItem.Background = highlightBrush;
            var animation = new ColorAnimation
            {
                To = Colors.Transparent,
                Duration = TimeSpan.FromMilliseconds(800),
                BeginTime = TimeSpan.FromMilliseconds(300),
                EasingFunction = new QuadraticEase
                {
                    EasingMode = EasingMode.EaseOut
                }
            };
            highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
        }
        else
        {
            // Vorhandenes Item hervorheben
            var existingItem = Excluded_Folders_Listbox.Items.OfType<ListBoxItem>().FirstOrDefault(item => item.Content?.ToString().Equals(folderNameOnly, StringComparison.OrdinalIgnoreCase) == true);
            if (existingItem != null)
            {
                Excluded_Folders_Listbox.UpdateLayout();
                Excluded_Folders_Listbox.ScrollIntoView(existingItem);
                var originalBrush = existingItem.Background as SolidColorBrush;
                if (originalBrush == null || originalBrush.IsFrozen)
                    originalBrush = new SolidColorBrush(Colors.Transparent);
                var highlightBrush = new SolidColorBrush(Colors.IndianRed);
                existingItem.Background = highlightBrush;
                var animation = new ColorAnimation
                {
                    To = originalBrush.Color,
                    Duration = TimeSpan.FromMilliseconds(600),
                    BeginTime = TimeSpan.FromMilliseconds(300),
                    EasingFunction = new QuadraticEase
                    {
                        EasingMode = EasingMode.EaseInOut
                    }
                };
                highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
            }
        }

        AddFolderNamePopup.IsOpen = false;
    }

    private string _pendingSelectedPath = null;

    ///
    /// ||======================================================================================================||
    /// || ====== DE: Button zum Bestätigen der Hinzufügung von Ordnerpfaden und prüft ob schon vorhanden ======||
    /// || ======     EN: Button to Confirm the Addition of Folder Paths and Check if already Exists      ======||
    /// ||======================================================================================================||
    ///     
    private void btnConfirmAddFolderPath_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var folderTreeView = (TreeView)window.FindName("FolderTreeViewPath");
        var driveTreeView = (TreeView)window.FindName("DriveTreeViewPath");
        var WarningPopup = (Popup)window.FindName("WarningPopup");
        string selectedPath = null;
        if (folderTreeView?.SelectedItem is TreeViewItem folderItem)
        {
            selectedPath = folderItem.Tag?.ToString();
        }
        else if (driveTreeView?.SelectedItem is TreeViewItem driveItem)
        {
            selectedPath = driveItem.Tag?.ToString();
        }

        if (string.IsNullOrWhiteSpace(selectedPath))
            return;
        if (selectedPath.Length == 3 && selectedPath[1] == ':' && selectedPath[2] == '\\' && char.IsLetter(selectedPath[0]))
        {
            _pendingSelectedPath = selectedPath;
            WarningPopup.IsOpen = true;
            LoadPopupIcons(WarningPopup);
        }
        else
        {
            AddSelectedPathToListbox(selectedPath);
        }
    }


    private void btnWarningYes_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var Allowed_Paths_Listbox = (ListBox)window.FindName("Allowed_Paths");
        var WarningPopup = (Popup)window.FindName("WarningPopup");
        var AddFolderPathPopup = (Popup)window.FindName("AddFolderPathPopup");
        if (!string.IsNullOrWhiteSpace(_pendingSelectedPath))
        {
            AddSelectedPathToListbox(_pendingSelectedPath);
            _pendingSelectedPath = null;
        }

        //AddFolderPathPopup.IsOpen = false;
        WarningPopup.IsOpen = false;
    }

    
    private void btnWarningNo_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var WarningPopup = (Popup)window.FindName("WarningPopup");
        _pendingSelectedPath = null;
        WarningPopup.IsOpen = false;
    }



    ///
    /// ||==================================================||
    /// || ====== DE: Ordnerpfad zur Liste hinzufügen ======||
    /// || ======   EN: Add Folder Path to Listbox    ======||
    /// ||==================================================||
    /// 
    private void AddSelectedPathToListbox(string selectedPath)
    {
        var window = Application.Current.MainWindow;
        var Allowed_Paths_Listbox = (ListBox)window.FindName("Allowed_Paths");
        // Duplikate prüfen
        bool alreadyExists = Allowed_Paths_Listbox.Items.OfType<ListBoxItem>().Any(item => item.Content?.ToString() == selectedPath);
        if (!alreadyExists)
        {
            var newItem = new ListBoxItem
            {
                Content = selectedPath
            };
            Allowed_Paths_Listbox.Items.Add(newItem);
            Allowed_Paths_Listbox.UpdateLayout(); // wichtig für ScrollIntoView
            Allowed_Paths_Listbox.ScrollIntoView(newItem);
            // Grünes Highlight animieren
            var highlightBrush = new SolidColorBrush(Colors.LightGreen);
            newItem.Background = highlightBrush;
            var animation = new ColorAnimation
            {
                To = Colors.Transparent,
                Duration = TimeSpan.FromMilliseconds(800),
                BeginTime = TimeSpan.FromMilliseconds(300),
                EasingFunction = new QuadraticEase
                {
                    EasingMode = EasingMode.EaseOut
                }
            };
            highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
        }
        else
        {
            // Highlight vorhandenes Item
            var existingItem = Allowed_Paths_Listbox.Items.OfType<ListBoxItem>().FirstOrDefault(item => item.Content?.ToString() == selectedPath);
            if (existingItem != null)
            {
                // Aktueller oder transparenter Hintergrund
                var originalBrush = existingItem.Background as SolidColorBrush;
                if (originalBrush == null || originalBrush.IsFrozen)
                    originalBrush = new SolidColorBrush(Colors.Transparent);
                // Neues Brush starten mit Rot
                var highlightBrush = new SolidColorBrush(Colors.IndianRed);
                existingItem.Background = highlightBrush;
                // Ziel-Farbe ist Originalfarbe
                Color toColor = originalBrush.Color;
                // Animationsdefinition
                var animation = new ColorAnimation
                {
                    To = toColor,
                    Duration = TimeSpan.FromMilliseconds(600),
                    BeginTime = TimeSpan.FromMilliseconds(300),
                    EasingFunction = new QuadraticEase
                    {
                        EasingMode = EasingMode.EaseInOut
                    }
                };
                // Animation starten
                highlightBrush.BeginAnimation(SolidColorBrush.ColorProperty, animation);
            }
        }
    }

    
    private void btnCancelAddFolderPath_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var AddFolderPathPopup = (Popup)window.FindName("AddFolderPathPopup");
        AddFolderPathPopup.IsOpen = false;
    }

    private void btnCancelAddFolderName_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var AddFolderNamePopup = (Popup)window.FindName("AddFolderNamePopup");
        AddFolderNamePopup.IsOpen = false;
    }

    ///
    /// ||=====================================================================||
    /// || ====== DE: Button öffnet Popup für Hinzufügen von Ordnernamen ======||
    /// || ======       EN: Button Opens Popup to Add Folder Names       ======||
    /// ||=====================================================================||   
    /// 
    private void AddFolderNamePopup_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var AddFolderNamePopup = (Popup)window.FindName("AddFolderNamePopup");
        LoadDrives(sender, "Name");
        if (AddFolderNamePopup != null)
        {
            AddFolderNamePopup.IsOpen = true; //Popup öffnen
            //LoadingIcons();
            LoadPopupIcons(AddFolderNamePopup);
            // ScrollViewer nach Öffnen des Popups binden
            AddFolderNamePopup.Dispatcher.InvokeAsync(() =>
            {
                if (AddFolderNamePopup.Child is DependencyObject popupRoot)
                {
                    var driveScrollViewer = FindChild<ScrollViewer>(popupRoot, "DriveTreeViewScrollViewer");
                    var folderScrollViewer = FindChild<ScrollViewer>(popupRoot, "FolderTreeViewScrollViewer");
                    if (driveScrollViewer != null)
                        driveScrollViewer.PreviewMouseWheel += ScrollViewer_PreviewMouseWheel;
                    if (folderScrollViewer != null)
                        folderScrollViewer.PreviewMouseWheel += ScrollViewer_PreviewMouseWheel;
                }
            });
        }
        else
        {
            MessageBox.Show("Add Name Popup not found.");
        }
    }

    ///
    /// ||======================================================================||
    /// || ====== DE: Button öffnet Popup für Hinzufügen von Ordnerpfaden ======||
    /// || ======       EN: Button Opens Popup to Add Folder Paths        ======||
    /// ||======================================================================||
    ///    
    private void AddFolderPathPopup_Click(object sender, RoutedEventArgs e)
    {
        var window = GetWindowFromSender(sender);
        var AddFolderPathPopup = (Popup)window.FindName("AddFolderPathPopup");
        LoadDrives(sender, "Path");
        if (AddFolderPathPopup != null)
        {
            AddFolderPathPopup.IsOpen = true; // Popup öffnen
            //LoadingIcons();
            LoadPopupIcons(AddFolderPathPopup);
            // ScrollViewer nach Öffnen des Popups binden
            AddFolderPathPopup.Dispatcher.InvokeAsync(() =>
            {
                if (AddFolderPathPopup.Child is DependencyObject popupRoot)
                {
                    var drivePathScrollViewer = FindChild<ScrollViewer>(popupRoot, "DriveTreeViewPathScrollViewer");
                    var folderPathScrollViewer = FindChild<ScrollViewer>(popupRoot, "FolderTreeViewPathScrollViewer");
                    if (drivePathScrollViewer != null)
                        drivePathScrollViewer.PreviewMouseWheel += ScrollViewer_PreviewMouseWheel;
                    if (folderPathScrollViewer != null)
                        folderPathScrollViewer.PreviewMouseWheel += ScrollViewer_PreviewMouseWheel;
                }
            });
        }
        else
        {
            MessageBox.Show("Add Folder Path Popup not found.");
        }
    }


    ///
    /// ||==================================================================================||
    /// || ====== DE: Seiten Anzeige mit Slide Animation von verschiedenen Richtungen ======||
    /// || ======   EN: Page Display with Slide Animation from Different Directions   ======||
    /// ||==================================================================================||
    /// 
    public enum SlideDirection
    {
        Left,
        Right,
        Top,
        Bottom
    }

    private const double SlideDistance = 650;      // feste Slide-Distanz
    private const int SlideDurationMs = 300;       // feste Dauer

    public void ShowOverlay(Grid overlay, SlideDirection direction = SlideDirection.Left)
    {
        overlay.Visibility = Visibility.Visible;

        overlay.Dispatcher.BeginInvoke(new Action(() =>
        {
            var transform = overlay.RenderTransform as TranslateTransform;
            if (transform == null)
                overlay.RenderTransform = transform = new TranslateTransform();

            double fromX = 0, fromY = 0;

            switch (direction)
            {
                case SlideDirection.Left:  fromX = -SlideDistance; break;
                case SlideDirection.Right: fromX = SlideDistance;  break;
                case SlideDirection.Top:   fromY = -SlideDistance; break;
                case SlideDirection.Bottom:fromY = SlideDistance;  break;
            }

            var animX = new DoubleAnimation(fromX, 0, TimeSpan.FromMilliseconds(SlideDurationMs))
            { EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut } };

            var animY = new DoubleAnimation(fromY, 0, TimeSpan.FromMilliseconds(SlideDurationMs))
            { EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut } };

            transform.BeginAnimation(TranslateTransform.XProperty, animX);
            transform.BeginAnimation(TranslateTransform.YProperty, animY);
        }), DispatcherPriority.Loaded);
    }

    public void HideOverlay(Grid overlay, SlideDirection direction = SlideDirection.Left)
    {
        var transform = overlay.RenderTransform as TranslateTransform;
        if (transform == null)
            overlay.RenderTransform = transform = new TranslateTransform();

        double toX = 0, toY = 0;

        switch (direction)
        {
            case SlideDirection.Left:  toX = -SlideDistance; break;
            case SlideDirection.Right: toX = SlideDistance;  break;
            case SlideDirection.Top:   toY = -SlideDistance; break;
            case SlideDirection.Bottom:toY = SlideDistance;  break;
        }

        var animX = new DoubleAnimation(transform.X, toX, TimeSpan.FromMilliseconds(SlideDurationMs))
        { EasingFunction = new CubicEase { EasingMode = EasingMode.EaseIn } };

        var animY = new DoubleAnimation(transform.Y, toY, TimeSpan.FromMilliseconds(SlideDurationMs))
        { EasingFunction = new CubicEase { EasingMode = EasingMode.EaseIn } };

        animX.Completed += (s, e) => overlay.Visibility = Visibility.Collapsed;

        transform.BeginAnimation(TranslateTransform.XProperty, animX);
        transform.BeginAnimation(TranslateTransform.YProperty, animY);
    }


    ///
    /// ||============================================================||
    /// || ====== DE: Funktion zum Verschieben von allen Popups ======||
    /// || ======   EN: Function to Drag and Move all Popups    ======||
    /// ||========================== Start ===========================||
    ///
    private bool _isDraggingPopup;
    private Point _screenStartMousePosition;
    private double _initialLeft;
    private double _initialTop;
    private Popup _activePopup;
    private readonly string[] _popupNames = new[]
    {
        "AddFolderNamePopup",
        "AddFolderPathPopup",
        "ExeNamePopup",
        "SettingsPopup",
        "HelpPopup",
        "SavePopup",
        "WarningPopup",
        "DeletePopup"
    };
    private Popup GetOpenPopup(Window window)
    {
        foreach (var popupName in _popupNames)
        {
            var popup = window.FindName(popupName) as Popup;
            if (popup != null && popup.IsOpen)
            {
                return popup;
            }
        }

        return null;
    }


    private void PopupHeaderDragArea_MouseLeftButtonDown1(object sender, MouseButtonEventArgs e)
    {
        e.Handled = true;
        var dragElement = (UIElement)sender;
        var popup = (dragElement as FrameworkElement)?.Tag as Popup;
        if (popup != null)
        {
            _isDraggingPopup = true;
            _activePopup = popup;
            _screenStartMousePosition = dragElement.PointToScreen(e.GetPosition(dragElement));
            _initialLeft = popup.HorizontalOffset;
            _initialTop = popup.VerticalOffset;
            dragElement.CaptureMouse();
        }
    }

    private void PopupHeaderDragArea_MouseMove(object sender, MouseEventArgs e)
    {
        if (_isDraggingPopup && e.LeftButton == MouseButtonState.Pressed && _activePopup != null && _activePopup.IsOpen)
        {
            Point currentScreenPos = ((UIElement)sender).PointToScreen(e.GetPosition((UIElement)sender));
            Vector delta = currentScreenPos - _screenStartMousePosition;
            _activePopup.HorizontalOffset = _initialLeft + delta.X;
            _activePopup.VerticalOffset = _initialTop + delta.Y;
        }
    }

    private void PopupHeaderDragArea_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
    {
        _isDraggingPopup = false;
        _activePopup = null;
        ((UIElement)sender).ReleaseMouseCapture();
    }
    ///
    /// ||================================================ End ================================================||
    ///     




    /// == DE: Öffnet den Standardbrowser mit der angegebenen URL | EN: Opens the default browser with the specified URL ==
    private void Hyperlink_RequestNavigate(object sender, RequestNavigateEventArgs e)
    {
        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = e.Uri.AbsoluteUri,
            UseShellExecute = true
        };
        Process.Start(psi);
        e.Handled = true;
    }

    ///
    /// ||==============================================================||
    /// || ====== DE: Prüft auf Updates und zeigt das Overlay an ====== ||
    /// || ======  EN: Checks for updates and shows the overlay  ====== ||
    /// ||==============================================================||
    /// 
    private void btnCheckUpdate_Click(object sender, RoutedEventArgs e)
    {
        _checkUpdateInvokedByButton = true;
        ResetUpdateOverlay();
        //ScanCategorySwitcherAsync();
        CheckUpdate();
        LoadingIcons();
        
        _checkUpdateInvokedByButton = false; // optional, falls du das Flag nur temporär brauchst
    }


    /// == DE: Öffnet die Github-Seite zum manuellen Download der neuesten Version | EN: Opens the Github page to manually Download the latest Version ==
    private void btnGithub_Click(object sender, RoutedEventArgs e)
    {
        string url = "https://github.com/stevo-ko/Category_Switcher/releases/latest";
        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = url,
            UseShellExecute = true
        };
        Process.Start(psi);
        e.Handled = true;
    }

    ///
    /// || ============================================================================ ||
    /// || ====== DE: Bricht den Download ab und löscht die unvollständige Datei ====== ||
    /// || ======    EN: Cancels the download and deletes the incomplete file    ====== ||
    /// || ============================================================================ ||
    /// 
    private void btnCancelDownload_Click(object sender, RoutedEventArgs e)
    {
        _cancelDownload = true;
    }

    private async void btnUpdate_Click(object sender, RoutedEventArgs e)
    {
        await ScanCategorySwitcherAsync();
        Window w = GetWindowFromSender(sender);
        var cancelButton = (Button)w.FindName("btnCancelDownload");

        var img = cancelButton.Content as Image;

        if (img == null && cancelButton.Content is Panel p)
        {
            img = p.Children.OfType<Image>().FirstOrDefault();

        }

        string localPath = Path.Combine(FolderPath ?? "", "_internal", "Assets", "cancel.png");

        if (File.Exists(localPath))
        {
            try
            {
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                bmp.UriSource = new Uri(localPath, UriKind.Absolute);
                bmp.EndInit();
                bmp.Freeze(); 

                img.Source = bmp;

            }
            catch (Exception ex)
            {
                MessageBox.Show($"[DEBUG] Fehler beim Laden lokaler Datei:\n{ex.Message}", "Fehler");
            }
        }
        else
        {

            try
            {
                img.Source = new BitmapImage(new Uri(
                    "https://img.icons8.com/?size=100&id=fYgQxDaH069W&format=png&color=000000"));
            }
            catch (Exception ex)
            {
                MessageBox.Show($"[DEBUG] Fehler beim Setzen des Fallback-Bildes:\n{ex.Message}", "Fehler");
            }
        }

        string wantedAssetName = "Category_Switcher.zip";
        _cancelDownload = false;
        try
        {
            await DownloadUpdateAsync(wantedAssetName);
        }
        catch (OperationCanceledException)
        {
            var window = Application.Current.MainWindow;
            var ProgressText = (TextBlock)window.FindName("ProgressText");
            ProgressText.Text = "Download abgebrochen!";
        }
    }

    ///
    /// ||================================================================================================||
    /// || ====== DE: Lädt das Update herunter, zeigt den Fortschritt an und startet den Installer ====== ||
    /// || ======        EN: Downloads the update, shows progress, and starts the installer        ====== ||
    /// ||================================================================================================||
    /// 
    public async Task DownloadUpdateAsync(string wantedAssetName)
    {

        if (_categorySwitcherPids != null && _categorySwitcherPids.Any())
        {
            MessageBox.Show($"Gefunden: {_categorySwitcherPids.Count} Category_Switcher Prozesse.");
            foreach (var pid in _categorySwitcherPids.ToList())
            {
                
                try
                {
                    var proc = Process.GetProcessById(pid);
                    proc.Kill();
                    proc.WaitForExit();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Fehler beim Beenden: {ex.Message}");
                }
            }

            _categorySwitcherPids.Clear();
        }

        var window = Application.Current.MainWindow;
        var DownloadProgressSection = (StackPanel)window.FindName("DownloadProgressSection");
        var ProgressBarBorder = (Border)window.FindName("ProgressBar");
        var ProgressPercent = (TextBlock)window.FindName("ProgressPercent");
        var ProgressText = (TextBlock)window.FindName("ProgressText");
        var ChangelogBorder = (Border)window.FindName("Changelog");
        var updateImport = (Border)window.FindName("UpdateImport");
        var CancelDownload = (Button)window.FindName("btnCancelDownload");
        var GithubBtn = (Button)window.FindName("btnGithub");
        var Update = (Button)window.FindName("btnUpdate");
        //string FolderPathTest = Path.Combine(FolderPath, "Test");
        string zipPath = Path.Combine(FolderPath, wantedAssetName);
        // Sprachstrings laden
        var langJsonUpdate = File.ReadAllText(LanguagePath);
        // Schritt 2: JSON deserialisieren
        var langObjUpdate = JObject.Parse(langJsonUpdate);
        // Nur Update_Overlay extrahieren
        var updateOverlayToken = langObjUpdate["Update_Overlay"];
        var updateStrings = updateOverlayToken.ToObject<Dictionary<string, string>>();
        // Storyboards
        var fadeOut = (Storyboard)ChangelogBorder.Resources["FadeOutStoryboard"];
        // Falls Changelog sichtbar, ausblenden
        GithubBtn.Visibility = Visibility.Collapsed;
        if (ChangelogBorder.Visibility == Visibility.Visible)
        {
            fadeOut.Completed += (s, ev) => ChangelogBorder.Visibility = Visibility.Collapsed;
            fadeOut.Begin(ChangelogBorder);
        }

        await Task.Delay(200);
        //GithubBtn.Visibility = Visibility.Collapsed;
        CancelDownload.Visibility = Visibility.Visible;
        
        _cancelDownload = false;
        try
        {
            // Reset UI für neuen Download
            await window.Dispatcher.InvokeAsync(() =>
            {

                //DownloadProgressSection.Visibility = Visibility.Visible;
                
                DownloadProgressSection.Visibility = Visibility.Visible;

                ProgressBarBorder.Visibility = Visibility.Visible;
                ProgressPercent.Visibility = Visibility.Visible;
                ProgressText.Visibility = Visibility.Visible;
                updateImport.Visibility = Visibility.Collapsed;
                var fadeIn = (Storyboard)DownloadProgressSection.Resources["FadeInProgressStoryboard"];
                fadeIn.Begin();
                // ProgressBar wieder auf ursprünglichen Gradient zurücksetzen
                var normalGradient = (LinearGradientBrush)window.Resources["ProgressGradient"];
                ProgressBarBorder.Background = normalGradient;
                // Fortschrittsanzeige zurücksetzen
                ProgressBarBorder.Width = 0;
                ProgressPercent.Text = "0%";
                ProgressText.Foreground = Brushes.LightGray;
                ProgressText.FontWeight = FontWeights.Normal;
                ProgressText.Text = updateStrings["Progresstext"].Replace("{current}", "0").Replace("{total}", "0");
            });
            using (var client = new HttpClient())
            {
                client.DefaultRequestHeaders.Add("User-Agent", "UpdateChecker");
                var response = await client.GetStringAsync($"https://api.github.com/repos/stevo-ko/Category_Switcher/releases/latest");
                var json = JObject.Parse(response);
                var assets = json["assets"];
                if (assets == null || !assets.HasValues)
                {
                    MessageBox.Show(updateStrings["No_Update"]);
                    return;
                }

                JToken asset = assets.FirstOrDefault(a => a["name"]?.ToString() == wantedAssetName);
                if (asset == null)
                {
                    MessageBox.Show($"Asset '{wantedAssetName}' nicht gefunden!");
                    return;
                }

                var assetUrl = asset["browser_download_url"]?.ToString();
                if (!Directory.Exists(FolderPath))
                    Directory.CreateDirectory(FolderPath);
                // Download
                using (var responseMsg = await client.GetAsync(assetUrl, HttpCompletionOption.ResponseHeadersRead))
                {
                    responseMsg.EnsureSuccessStatusCode();
                    var totalBytes = responseMsg.Content.Headers.ContentLength ?? 0;
                    var totalMB = totalBytes / 1024.0 / 1024.0;
                    double downloadedBytes = 0;
                    using (var stream = await responseMsg.Content.ReadAsStreamAsync())
                    using (var fs = new FileStream(zipPath, FileMode.Create, FileAccess.Write, FileShare.None))
                    {
                        byte[] buffer = new byte[8192];
                        int read;
                        while ((read = await stream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                        {
                            if (_cancelDownload)
                                break;
                            await fs.WriteAsync(buffer, 0, read);
                            downloadedBytes += read;
                            double percent = (double)downloadedBytes / totalBytes;
                            await window.Dispatcher.InvokeAsync(() =>
                            {
                                ProgressBarBorder.Width = 400 * percent;
                                ProgressPercent.Text = updateStrings["Downloadprogress"].Replace("{progress}", $"{percent * 100:F0}");
                                ProgressText.Text = updateStrings["Progresstext"].Replace("{current}", $"{downloadedBytes / 1024.0 / 1024.0:F2} MB").Replace("{total}", $"{totalMB:F2}");
                            });
                        }
                    }

                    if (_cancelDownload)
                    {
                        await window.Dispatcher.InvokeAsync(() =>
                        {
                            ProgressText.Text = updateStrings.ContainsKey("Download_Abort") ? updateStrings["Download_Abort"] : "Download abgebrochen!";
                            ProgressBarBorder.Background = new LinearGradientBrush(Colors.Red, Colors.DarkRed, 0);
                            ProgressText.Foreground = Brushes.Red;
                            ProgressText.FontWeight = FontWeights.Bold;
                        });
                        // Temporäre ZIP-Datei löschen
                        if (File.Exists(zipPath))
                            File.Delete(zipPath);

                        // Einfach return, keine Exception werfen
                        return;
                    }
                }

                // ZIP entpacken
                using (var stream = new FileStream(zipPath, FileMode.Open))
                using (var archive = new ZipArchive(stream, ZipArchiveMode.Read))
                {
                    int totalEntries = archive.Entries.Count;
                    int currentEntry = 0;
                    foreach (var entry in archive.Entries)
                    {
                        if (_cancelDownload)
                            break;
                        currentEntry++;

                        tempPath = Path.Combine(FolderPath, "Temp");
                        var destPath = Path.Combine(tempPath, entry.FullName);
                        var dir = Path.GetDirectoryName(destPath);
                        if (!Directory.Exists(dir))
                            Directory.CreateDirectory(dir);
                        if (!string.IsNullOrEmpty(entry.Name))
                        {
                            try
                            {
                                using (var entryStream = entry.Open())
                                using (var fileStream = new FileStream(destPath, FileMode.Create, FileAccess.Write, FileShare.ReadWrite))
                                {
                                    await entryStream.CopyToAsync(fileStream);
                                }
                            }
                            catch (IOException ioEx)
                            {
                                // Falls Datei gesperrt ist und PNG/ICO: überspringen
                                if (destPath.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                                    destPath.EndsWith(".ico", StringComparison.OrdinalIgnoreCase))
                                {
                                    // optional loggen
                                    Debug.WriteLine($"Übersprungen: {destPath} ({ioEx.Message})");
                                    continue;
                                }
                                else
                                {
                                    throw; // andere Dateien sollen den Fehler normal werfen
                                }
                            }
                        }

                        await window.Dispatcher.InvokeAsync(() =>
                        {
                            double percent = (double)currentEntry / totalEntries;
                            ProgressBarBorder.Width = 400 * percent;
                            ProgressPercent.Text = $"{percent * 100:F0}%";
                            ProgressText.Text = $"{updateStrings["Unpacking"]}: {entry.Name}";
                        });
                    }
                }

                if (_cancelDownload)
                {
                    // UI auf "abgebrochen" setzen
                    await window.Dispatcher.InvokeAsync(() =>
                    {
                        ProgressText.Text = updateStrings.ContainsKey("Unpacking_Abort") ? updateStrings["Unpacking_Abort"] : "Entpacken abgebrochen!";
                        ProgressBarBorder.Background = new LinearGradientBrush(Colors.Red, Colors.DarkRed, 0);
                        ProgressText.Foreground = Brushes.Red;
                        ProgressText.FontWeight = FontWeights.Bold;
                    });
                    // Alle geöffneten Streams vorher schließen
                    // Teilweise entpackte Dateien löschen
                    if (Directory.Exists(tempPath))
                        Directory.Delete(tempPath, true);
                    if (File.Exists(zipPath))
                        File.Delete(zipPath);

                    // Methode sauber verlassen
                    return;
                }

                // Dateien von Temp nach FolderPath verschieben
                try
                {
                    string tempPath = Path.Combine(FolderPath, "Temp");
                    if (Directory.Exists(tempPath))
                    {
                        var allFiles = Directory.GetFiles(tempPath, "*", SearchOption.AllDirectories);
                        var failedFiles = new List<string>();

                        foreach (var sourceFile in allFiles)
                        {
                            try
                            {
                                // Relativen Pfad ermitteln
                                string tempPathWithSlash = tempPath.EndsWith("\\") ? tempPath : tempPath + "\\";
                                string relativePath = sourceFile.Substring(tempPathWithSlash.Length);
                                string targetFile = Path.Combine(FolderPath, relativePath);

                                // Zielverzeichnis erstellen falls nötig
                                string targetDir = Path.GetDirectoryName(targetFile);
                                if (!Directory.Exists(targetDir))
                                    Directory.CreateDirectory(targetDir);

                                // Datei verschieben (überschreiben)
                                if (File.Exists(targetFile))
                                    File.Delete(targetFile);
                                
                                File.Move(sourceFile, targetFile);
                            }
                            catch (Exception ex)
                            {
                                // PNG und ICO Dateien bei Fehler ignorieren
                                if (sourceFile.EndsWith(".png", StringComparison.OrdinalIgnoreCase) ||
                                    sourceFile.EndsWith(".ico", StringComparison.OrdinalIgnoreCase))
                                {
                                    continue;
                                }
                                failedFiles.Add($"{Path.GetFileName(sourceFile)}: {ex.Message}");
                            }
                        }

                        // Fehler anzeigen falls welche aufgetreten sind
                        if (failedFiles.Count > 0)
                        {
                            string errorMessage = "Following files could not be moved:\n" +
                                                string.Join("\n", failedFiles);

                            await window.Dispatcher.InvokeAsync(() =>
                            {
                                MessageBox.Show(errorMessage, "Error when Moving",
                                              MessageBoxButton.OK, MessageBoxImage.Warning);
                            });
                        }
                        else
                        {
                            // Temp-Ordner löschen
                            try
                            {
                                Directory.Delete(tempPath, true);
                            }
                            catch { /* Ignorieren */ }
                        }
                    }
                }
                catch (Exception ex)
                {
                    await window.Dispatcher.InvokeAsync(() =>
                    {
                        MessageBox.Show($"Error moving files:\n{ex.Message}", 
                                      "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    });
                }

                // ZIP-Datei löschen
                if (File.Exists(zipPath))
                    File.Delete(zipPath);

                // Fertig
                ProgressBarBorder.Background = new LinearGradientBrush(Colors.Green, Colors.DarkGreen, 0);
                ProgressText.Text = updateStrings.ContainsKey("Update_Success") ? updateStrings["Update_Success"] : "Download abgeschlossen!";
                ProgressText.Foreground = Brushes.Green;
                ProgressText.FontWeight = FontWeights.Bold;
                if (HasUpdateImport)
                {
                    updateImport.Visibility = Visibility.Visible;
                }
                Update.Visibility = Visibility.Collapsed;
                CancelDownload.Visibility = Visibility.Collapsed;
                if (DidRun == true)
                {
                    CPH.RunAction("[STEVO] Open Category Switcher", true);
                }
            }
        }
        catch (Exception ex)
        {
            await window.Dispatcher.InvokeAsync(() =>
            {
                string errorMsg = updateStrings.ContainsKey("Update_Error") ? updateStrings["Update_Error"].Replace("{error}", ex.Message) : "Fehler beim Update: " + ex.Message;
                MessageBox.Show(errorMsg);
                ProgressBarBorder.Background = new LinearGradientBrush(Colors.Red, Colors.DarkRed, 0);
            });
        }
    }

    /// 
    /// ||=====================================================================||
    /// || ====== DE: Scannt nach laufenden Category_Switcher-Prozessen ====== ||
    /// || ======   EN: Scans for running Category_Switcher processes   ====== ||
    /// ||=====================================================================||
    /// 
    private async Task ScanCategorySwitcherAsync()
    {
        _categorySwitcherPids.Clear();
        await Task.Run(() =>
        {
            var processes = Process.GetProcessesByName("Category_Switcher");
            foreach (var process in processes)
            {
                try
                {
                    if (string.Equals(process.MainModule.FileName, _expectedCategorySwitcherPath, StringComparison.OrdinalIgnoreCase))
                    {
                        _categorySwitcherPids.Add(process.Id);
                    }
                }
                catch
                {
                // Ignorieren, falls kein Zugriff
                }
            }
        });
        // UI-Update
        currentWindow.Dispatcher.Invoke(() =>
        {
            if (_categorySwitcherPids.Any())
            {
                //MessageBox.Show($"Gefunden: {_categorySwitcherPids.Count} Category_Switcher Prozesse.");
                DidRun = true;
            }
            else
            {
                //MessageBox.Show("Kein Category_Switcher gefunden.");
                DidRun = false;
            }
        });
    }

    ///
    /// ||==================================================================||
    /// || ====== DE: Setzt alle Elemente des Update-Overlays zurück ====== ||
    /// || ======   EN: Resets all elements of the Update Overlay    ====== ||
    /// ||==================================================================||
    /// 
    private void ResetUpdateOverlay()
    {
        var window = Application.Current.MainWindow;
        // Overlay selbst
        var updateOverlay = (Grid)window.FindName("UpdateOverlay");
        updateOverlay.Visibility = Visibility.Collapsed;
        // Version-Anzeigen zurücksetzen
        ((TextBlock)window.FindName("UpdateVersionSetting")).Visibility = Visibility.Collapsed;
        ((TextBlock)window.FindName("UpdateVersionProgram")).Visibility = Visibility.Collapsed;
        ((TextBlock)window.FindName("ArrowProgram")).Visibility = Visibility.Collapsed;
        ((TextBlock)window.FindName("ArrowSettings")).Visibility = Visibility.Collapsed;
        ((Border)window.FindName("NoUpdate_Available")).Visibility = Visibility.Collapsed; 
        // Changelog zurücksetzen
        var changelogBorder = (Border)window.FindName("Changelog");
        if (changelogBorder != null)
        {
            // Animation stoppen / entfernen
            changelogBorder.BeginAnimation(UIElement.OpacityProperty, null);
            changelogBorder.BeginAnimation(UIElement.RenderTransformProperty, null);
            // RenderTransform zurücksetzen
            changelogBorder.RenderTransform = new TranslateTransform(0, 0);
            // Opacity direkt setzen
            changelogBorder.Opacity = 1.0;
            // Sichtbarkeit zurücksetzen
            changelogBorder.Visibility = Visibility.Collapsed;
        }

        var changelogText = (RichTextBox)window.FindName("ChangelogMarkdown");
        changelogText.Document.Blocks.Clear();
        changelogText.Document.Blocks.Add(new Paragraph(new Run("Noch keine Daten geladen...")));
        // Download Section zurücksetzen
        var downloadSection = (StackPanel)window.FindName("DownloadProgressSection");
        downloadSection.Visibility = Visibility.Collapsed;

        var updateImport = (Border)window.FindName("UpdateImport");
        updateImport.Visibility = Visibility.Collapsed;

        var progressBar = (Border)window.FindName("ProgressBar");
        progressBar.Width = 0;
        progressBar.Visibility = Visibility.Collapsed;
        var progressPercent = (TextBlock)window.FindName("ProgressPercent");
        progressPercent.Visibility = Visibility.Collapsed;
        progressPercent.Text = "0%";
        var progressText = (TextBlock)window.FindName("ProgressText");
        progressText.Visibility = Visibility.Collapsed;
        progressText.Text = "0 MB von 0 MB geladen";
        // Buttons
        ((Button)window.FindName("btnUpdate")).Visibility = Visibility.Collapsed;
        ((Button)window.FindName("btnGithub")).Visibility = Visibility.Collapsed;
        ((Button)window.FindName("btnCancelDownload")).Visibility = Visibility.Collapsed;
        _lastUpdateResult = null;
        _cancelDownload = true;
    }

    ///
    /// ||=============================================||
    /// || ====== DE: Ergebnisobjekt für Updates ======||
    /// || ======  EN: Result object for updates ======||
    /// ||============================================||
    ///
    public class UpdateResult
    {
        public bool ProgramUpdate { get; set; }
        public bool SettingsUpdate { get; set; }
        public string CurrentProgramVersion { get; set; }
        public string CurrentSettingsVersion { get; set; }
        public string RemoteProgramVersion { get; set; }
        public string RemoteSettingsVersion { get; set; }

        public bool HasUpdateImport { get; set; }
        public string Changelog { get; set; }
    }

    /// == DE: Version.json Inhalt | EN: Version.json content ==
    public class VersionInfo
    {
        [JsonProperty("ProgramVersion")]
        public string ProgramVersion { get; set; }

        [JsonProperty("SettingsVersion")]
        public string SettingsVersion { get; set; }
    }

    ///
    /// ||=================================================================================||
    /// || ====== DE: Funktion zum Prüfen ob ein Update verfügbar und anzuzeigen ist ======||
    /// || ======  EN: Function to check if an update is available and to display it ======||
    /// ||===================================== Start =====================================||
    /// 
    public UpdateResult CheckUpdate()
    {
        Window window = null !;
        TextBlock UpdateSettingsVersion = null !;
        TextBlock UpdateProgramVersion = null !;
        TextBlock ArrowProgram = null !;
        TextBlock ArrowSettings = null !;
        window = Application.Current.MainWindow;
        //LocalVersionFile = null!;
        if (_checkUpdateInvokedByButton)
        {
            // Wurde durch Button aufgerufen
            //MessageBox.Show("CheckUpdate durch Button ausgeführt");
            UpdateSettingsVersion = (TextBlock)window.FindName("UpdateVersionSetting");
            UpdateProgramVersion = (TextBlock)window.FindName("UpdateVersionProgram");
            ArrowProgram = (TextBlock)window.FindName("ArrowProgram");
            ArrowSettings = (TextBlock)window.FindName("ArrowSettings");
            ((Grid)window.FindName("AboutOverlay")).Visibility = Visibility.Hidden;
            ((Grid)window.FindName("UpdateOverlay")).Visibility = Visibility.Visible;
            var LocalVersionFile = "";
            if (_lastUpdateResult != null)
            {
                // --- Program Update ---
                if (_lastUpdateResult.ProgramUpdate)
                {
                    ArrowProgram.Visibility = Visibility.Visible;
                    UpdateProgramVersion.Visibility = Visibility.Visible;
                    UpdateProgramVersion.Text = "v" + remoteProgramVersion;
                }

                // --- Settings Update ---
                if (_lastUpdateResult.SettingsUpdate)
                {
                    ArrowSettings.Visibility = Visibility.Visible;
                    UpdateSettingsVersion.Visibility = Visibility.Visible;
                    UpdateSettingsVersion.Text = "v" + remoteSettingsVersion;
                }

                // --- Gemeinsamer Changelog ---
                if ((_lastUpdateResult.ProgramUpdate || _lastUpdateResult.SettingsUpdate) && !string.IsNullOrWhiteSpace(_lastUpdateResult.Changelog))
                {
                    //var changelogTextBlock = (TextBlock)window.FindName("ChangelogText");
                    var changelogBorder = (Border)window.FindName("Changelog");
                    //if (changelogTextBlock != null)
                    //    changelogTextBlock.Text = _lastUpdateResult.Changelog;

                    if (changelogBorder != null)
                        changelogBorder.Visibility = Visibility.Visible;

                    var btnUpdate = (Button)window.FindName("btnUpdate");
                    if (btnUpdate != null)
                        btnUpdate.Visibility = Visibility.Visible;

                    var changelogBox = (RichTextBox)window.FindName("ChangelogMarkdown");
                    string markdown = NormalizeNestedDashLists(_lastUpdateResult.Changelog);
                    markdown = NormalizeMarkdown(markdown);
                    var emojiMap = BuildGitHubEmojiUrlMap();
                    SetMarkdownToRichTextBoxRich(changelogBox, markdown, emojiMap);
                    if (_lastUpdateResult.HasUpdateImport)
                    {
                        HasUpdateImport = true;
                    }
                    //MessageBox.Show($"Updatestevo: {HasUpdateImport}");
                    }

                return _lastUpdateResult;
            }
        }
        else
        {
            // Wurde direkt im Code aufgerufen
            //MessageBox.Show("CheckUpdate direkt aus Code aufgerufen");
            // Pfad aus Streamer.bot global var
            FolderPath = CPH.GetGlobalVar<string>("[STEVO] SettingsPath", true);
            if (string.IsNullOrWhiteSpace(FolderPath))
            {
                CPH.RunAction("[STEVO] Open Category Switcher", true);
            //Thread.Sleep(10000);
            }

            LocalVersionFile = Path.Combine(FolderPath, "Version.json");
        }

        var GithubApiUrl = "https://api.github.com/repos/stevo-ko/Category_Switcher/releases/latest";
        var result = new UpdateResult
        {
            ProgramUpdate = false,
            SettingsUpdate = false
        };
        try
        {

            if (!File.Exists(LocalVersionFile))
            {
                MessageBox.Show("Version.json nicht gefunden!", "Debug", MessageBoxButton.OK, MessageBoxImage.Warning);
            }

            var localJson = File.ReadAllText(LocalVersionFile);
            //MessageBox.Show("json read");
            var localVersion = JsonConvert.DeserializeObject<VersionInfo>(localJson);
            ((TextBlock)window.FindName("YourVersionSettings")).Text = "v" + localVersion.SettingsVersion;
            ((TextBlock)window.FindName("YourVersionProgram")).Text = "v" + localVersion.ProgramVersion;
            //MessageBox.Show($"Lokale Versionen geladen:\n" + $"Programm: {localVersion.ProgramVersion}\n" + $"Settings: {localVersion.SettingsVersion}","Debug", MessageBoxButton.OK, MessageBoxImage.Information);
            // TLS 1.2 erzwingen
            string response = null;
            try
            {
                // TLS 1.2 erzwingen
                System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

                using var client = new HttpClient();
                client.DefaultRequestHeaders.UserAgent.ParseAdd("SettingsMenuUpdater/1.0");
                response = client.GetStringAsync(GithubApiUrl).Result; 

            }
            catch (AggregateException agg) when (agg.InnerException is HttpRequestException httpEx &&
                                                httpEx.Message.Contains("403"))
            {
                CPH.LogWarn("GitHub API Rate Limit erreicht! Warte etwas oder nutze ein Token.");
                ((Border)window.FindName("RateLimit")).Visibility = Visibility.Visible;
            }

            catch (Exception ex)
            {
                MessageBox.Show($"Fehler beim HTTP Request:\n{ex}");
            }

            var remoteJson = JObject.Parse(response);
            var tag = remoteJson["tag_name"]?.ToString();
            if (string.IsNullOrEmpty(tag))
            {
            MessageBox.Show("Kein tag_name im GitHub-JSON gefunden!", "Debug", MessageBoxButton.OK, MessageBoxImage.Warning);
            }

            //MessageBox.Show($"Gefundener Release-Tag: {tag}", "Debug", MessageBoxButton.OK, MessageBoxImage.Information);
            var match = Regex.Match(tag, @"v(?<prog>[\d\.]+)-Sv(?<set>[\d\.]+)");
            if (!match.Success)
            {
            MessageBox.Show($"Regex hat nicht gepasst für Tag: {tag}", "Debug", MessageBoxButton.OK, MessageBoxImage.Warning);
            }

            var updateimport = remoteJson["assets"] as JArray;
            if (updateimport != null)
            {
                foreach (var asset in updateimport)
                {
                    string name = asset["name"]?.ToString() ?? "";
                    if (name.Equals("Update.stevo", StringComparison.OrdinalIgnoreCase))
                    {
                        result.HasUpdateImport = true;
                        HasUpdateImport = result.HasUpdateImport;
                        CPH.LogInfo($"Update.stevo gefunden: {result.HasUpdateImport}");
                        break;
                    }
                }
            }


            if (_checkUpdateInvokedByButton)
            {
                remoteProgramVersion = match.Groups["prog"].Value;
                remoteSettingsVersion = match.Groups["set"].Value;
            }
            else
            {
                remoteProgramVersion = match.Groups["prog"].Value;
                remoteSettingsVersion = match.Groups["set"].Value;
            }

            result.RemoteProgramVersion = remoteProgramVersion;
            result.RemoteSettingsVersion = remoteSettingsVersion;
            //MessageBox.Show($"Remote Versionen:\n" + $"Programm: {remoteProgramVersion}\n" + $"Settings: {remoteSettingsVersion}","Debug", MessageBoxButton.OK, MessageBoxImage.Information);
            result.ProgramUpdate = new Version(remoteProgramVersion) > new Version(localVersion.ProgramVersion);
            result.SettingsUpdate = new Version(remoteSettingsVersion) > new Version(localVersion.SettingsVersion);
           

            //MessageBox.Show($"Update-Check Ergebnis:\n" + $"Programm Update: {result.ProgramUpdate}\n" + $"Settings Update: {result.SettingsUpdate}", "Debug", MessageBoxButton.OK, MessageBoxImage.Information);
            // Release Notes auslesen
            var changelog = remoteJson["body"]?.ToString() ?? "Kein Changelog vorhanden";

            // Sprache auswählen ("DE" oder "EN")
            string lang = _ViewModel.currentLang;

            // Regex: suche ## v3.0-Sv1.5 (DE) + alles bis zum nächsten ## v... oder Ende
            string pattern = $@"(##\s+.*\*\*{Regex.Escape(tag)}\s+\({lang}\)\*\*[\s\S]*?)(?=^##\s+.*\*\*v|\Z)";


            var matchchangelog = Regex.Match(changelog, pattern, RegexOptions.Multiline | RegexOptions.IgnoreCase);

            if (matchchangelog.Success)
            {
                // Ganze Section inkl. Überschrift übernehmen
                string section = matchchangelog.Groups[1].Value.Trim();

                // Sprache-Code aus der Überschrift entfernen: z.B. "## v3.0-Sv1.5 (DE)" -> "## v3.0-Sv1.5"
                section = Regex.Replace(section, $@"(\*\*{Regex.Escape(tag)})\s+\({lang}\)(\*\*)", "$1$2", RegexOptions.Multiline);
                result.Changelog = section;

            }
            else
            {
                result.Changelog = "Kein Changelog für die Sprache gefunden.";
            }

            if (_checkUpdateInvokedByButton)
            {
                // --- Program Update ---
                if (result.ProgramUpdate)
                {
                    ArrowProgram.Visibility = Visibility.Visible;
                    UpdateProgramVersion.Visibility = Visibility.Visible;
                    UpdateProgramVersion.Text = "v" + remoteProgramVersion;
                }

                // --- Settings Update ---
                if (result.SettingsUpdate)
                {
                    ArrowSettings.Visibility = Visibility.Visible;
                    UpdateSettingsVersion.Visibility = Visibility.Visible;
                    UpdateSettingsVersion.Text = "v" + remoteSettingsVersion;
                }

                // --- Gemeinsamer Changelog ---
                if ((result.ProgramUpdate || result.SettingsUpdate) && !string.IsNullOrWhiteSpace(result.Changelog))
                {

                    var changelogBorder = (Border)window.FindName("Changelog");

                    if (changelogBorder != null)
                        changelogBorder.Visibility = Visibility.Visible;

                    var btnUpdate = (Button)window.FindName("btnUpdate");
                    if (btnUpdate != null)
                        btnUpdate.Visibility = Visibility.Visible;
                    var btnGithub = (Button)window.FindName("btnGithub");
                    if (btnGithub != null)
                        btnGithub.Visibility = Visibility.Visible;

                    var changelogBox = (RichTextBox)window.FindName("ChangelogMarkdown");
                    string markdown = NormalizeNestedDashLists(result.Changelog);
                    markdown = NormalizeMarkdown(markdown);
                    var emojiMap = BuildGitHubEmojiUrlMap();
                    SetMarkdownToRichTextBoxRich(changelogBox, markdown, emojiMap);
                }
                else
                {
                    ((Border)window.FindName("NoUpdate_Available")).Visibility = Visibility.Visible;                    
                }
            }
            else
            {
                _lastUpdateResult = result;
                // Release Notes auslesen
                changelog = remoteJson["body"]?.ToString() ?? "Kein Changelog vorhanden";
                // Optional in UpdateResult speichern
                result.Changelog = changelog;
                Execute();
            }

            return result;
        }
        catch (Exception ex)
        {
            var inner = ex.InnerException?.Message ?? "Keine InnerException";
            //MessageBox.Show($"Fehler beim Abrufen der GitHub API:\n" + $"Typ: {ex.GetType()}\n" + $"Message: {ex.Message}\n" + $"Inner: {inner}","Debug Error",  MessageBoxButton.OK,MessageBoxImage.Error);
            return result;
        }
    }

    /// == DE: Erstellt eine Map für die GitHub-Emojis | EN: Creates a map for GitHub emojis ==
    static Dictionary<string, string> BuildGitHubEmojiUrlMap()
    {
        string url = "https://api.github.com/emojis";
        string json;
        using (var wc = new WebClient())
        {
            wc.Headers.Add("User-Agent", "EmojiReplace/1.0"); // GitHub verlangt das
            wc.Encoding = System.Text.Encoding.UTF8;
            json = wc.DownloadString(url);
        }

        var emojiMap = new Dictionary<string, string>();
        var obj = JObject.Parse(json);
        foreach (var prop in obj.Properties())
        {
            string alias = $":{prop.Name}:"; // z. B. ":smile:"
            string imgUrl = prop.Value.ToString();
            if (!emojiMap.ContainsKey(alias))
                emojiMap[alias] = imgUrl;
        }

        return emojiMap;
    }

    /// == DE: Normalisiert verschachtelte Dash-Listen in Markdown | EN: Normalizes nested dash lists in Markdown ==
    public static string NormalizeNestedDashLists(string markdown)
    {
        if (string.IsNullOrEmpty(markdown))
            return markdown;
        var lines = markdown.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
        var sb = new System.Text.StringBuilder();
        bool lastWasList = false;
        foreach (var rawLine in lines)
        {
            if (string.IsNullOrWhiteSpace(rawLine))
            {
                sb.AppendLine(rawLine);
                lastWasList = false;
                continue;
            }

            var leadingWsCount = rawLine.Length - rawLine.TrimStart().Length;
            var counttag = $"[{leadingWsCount}]";
            var leadingWs = rawLine.Substring(0, leadingWsCount);
            var trimmed = rawLine.TrimStart();
            int dashCount = 0;
            while (dashCount < trimmed.Length && trimmed[dashCount] == '-')
                dashCount++;
            if (dashCount > 0)
            {
                var rest = trimmed.Substring(dashCount);
                if (rest.Length == 0)
                {
                    sb.AppendLine(rawLine);
                    lastWasList = false;
                    continue;
                }

                var content = rest.TrimStart();
                int indentSpaces = Math.Max(0, (dashCount - 1) * 2);
                //sb.AppendLine(leadingWs + new string(' ', indentSpaces) + "- " + counttag + content);
                sb.AppendLine(leadingWs + new string (' ', indentSpaces) + "- " + content);
                lastWasList = true;
            }
            else
            {
                if (lastWasList)
                {
                    sb.AppendLine(); // Abstand nur hinzufügen, wenn wirklich nötig
                }

                sb.AppendLine(rawLine);
                lastWasList = false;
            }
        }

        return sb.ToString();
    }

    /// == DE: Normalisiert Markdown-Elemente in einem String | EN: Normalizes markdown elements in a string ==
    public static string NormalizeMarkdown(string markdown)
    {
        if (string.IsNullOrEmpty(markdown))
            return markdown;
        var lines = markdown.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None);
        var sb = new System.Text.StringBuilder();
        bool lastWasList = false;
        foreach (var rawLine in lines)
        {
            if (string.IsNullOrWhiteSpace(rawLine))
            {
                sb.AppendLine(rawLine);
                lastWasList = false;
                continue;
            }

            var leadingWsCount = rawLine.Length - rawLine.TrimStart().Length;
            var counttag = $"[{leadingWsCount}]";
            var leadingWs = rawLine.Substring(0, leadingWsCount);
            var trimmed = rawLine.TrimStart();
            // ### 1) Headings
            if (trimmed.StartsWith("#"))
            {
                int level = trimmed.TakeWhile(c => c == '#').Count();
                var content = trimmed.Substring(level).Trim();
                sb.AppendLine($"[Heading{Math.Min(level, 6)}] {content}");
                lastWasList = false;
                continue;
            }

            // ### 2) Quote
            if (trimmed.StartsWith(">"))
            {
                var content = trimmed.Substring(1).Trim();
                sb.AppendLine($"[QuoteBlock] {content}");
                lastWasList = false;
                continue;
            }

            // ### 3) Thematic Break
            if (trimmed.StartsWith("---") || trimmed.StartsWith("***"))
            {
                sb.AppendLine("[ThematicBreak]");
                lastWasList = false;
                continue;
            }

            // ### 4) CodeBlock (Erkennung nur Start/Ende)
            if (trimmed.StartsWith("```"))
            {
                sb.AppendLine("[CodeBlock]");
                lastWasList = false;
                continue;
            }

            // ### 5) Nested Dash Lists (dein ursprünglicher Teil)
            int dashCount = 0;
            while (dashCount < trimmed.Length && trimmed[dashCount] == '-')
                dashCount++;
            if (dashCount > 0)
            {
                var rest = trimmed.Substring(dashCount);
                if (rest.Length == 0)
                {
                    sb.AppendLine(rawLine);
                    lastWasList = false;
                    continue;
                }

                var content = rest.TrimStart();
                int indentSpaces = Math.Max(0, (dashCount - 1) * 2);
                //sb.AppendLine(leadingWs + new string(' ', indentSpaces) + "- " + counttag + content);
                sb.AppendLine(leadingWs + new string (' ', indentSpaces) + "- " + content);
                lastWasList = true;
                continue;
            }

            // ### 6) Fallback normaler Text
            if (lastWasList)
            {
                sb.AppendLine(); // Absatz nach Liste
            }

            sb.AppendLine(rawLine);
            lastWasList = false;
        }

        return sb.ToString();
    }

    /// == DE: Ersetzt Emojis mit Bildern in einem FlowDocument | EN: Replaces emojis with images in a FlowDocument ==
    void ReplaceEmojisWithImages(FlowDocument doc, Dictionary<string, string> emojiMap)
    {
        foreach (var block in doc.Blocks)
        {
            if (block is Paragraph para)
            {
                var inlines = para.Inlines.ToList(); // Kopie, weil wir während der Iteration ändern
                para.Inlines.Clear();
                foreach (var inline in inlines)
                {
                    if (inline is Run run)
                    {
                        string text = run.Text;
                        int lastIndex = 0;
                        var matches = Regex.Matches(text, @":([a-zA-Z0-9_+\-]+):"); // Shortcodes
                        foreach (Match match in matches)
                        {
                            string code = match.Value;
                            if (emojiMap.TryGetValue(code, out string url))
                            {
                                MessageBox.Show($"Gefunden: {code} → {url}");
                                var img = new Image
                                {
                                    Source = new BitmapImage(new Uri(url)),
                                    Width = 100,
                                    Height = 100
                                };
                                para.Inlines.Add(new InlineUIContainer(img));
                            }
                            else
                            {
                                MessageBox.Show($"Nicht gefunden: {code}");
                                para.Inlines.Add(new Run(code) { Foreground = run.Foreground, FontFamily = run.FontFamily });
                            }

                            // Text vor dem Emoji hinzufügen
                            if (match.Index > lastIndex)
                            {
                                para.Inlines.Add(new Run(text.Substring(lastIndex, match.Index - lastIndex)) { Foreground = run.Foreground, FontFamily = run.FontFamily });
                            }

                            lastIndex = match.Index + match.Length;
                        }

                        // Resttext nach letztem Emoji
                        if (lastIndex < text.Length)
                        {
                            para.Inlines.Add(new Run(text.Substring(lastIndex)) { Foreground = run.Foreground, FontFamily = run.FontFamily });
                        }
                    }
                    else
                    {
                        // Andere Inline-Typen wieder hinzufügen
                        para.Inlines.Add(inline);
                    }
                }
            }
        }
    }

    /// == DE: Setzt Markdown in ein RichTextBox mit Emoji-Unterstützung | EN: Sets markdown into a RichTextBox with emoji support ==
    public static void SetMarkdownToRichTextBoxRich(System.Windows.Controls.RichTextBox richTextBox, string markdown, Dictionary<string, string> emojiMap)
    {
        if (richTextBox == null)
            return;
        var pipeline = new Markdig.MarkdownPipelineBuilder().UseAdvancedExtensions().Build();
        var sourceDoc = Markdig.Wpf.Markdown.ToFlowDocument(markdown, pipeline);
        var targetDoc = new System.Windows.Documents.FlowDocument();
        // ================= Emoji-Ersetzung =================
        void ReplaceShortcodesWithImages(InlineCollection inlines, double fontSize, double? emojiSize = null, Thickness? emojiMargin = null, TranslateTransform? emojiOffset = null)
        {
            var margin = emojiMargin ?? new Thickness(0);
            var offset = emojiOffset ?? new TranslateTransform(0, 0); // Standard 0,0
            double effectiveEmojiSize = fontSize + (emojiSize ?? 12);
            var list = inlines.ToList();
            inlines.Clear();
            foreach (var inline in list)
            {
                switch (inline)
                {
                    case System.Windows.Documents.Run run:
                        string text = run.Text;
                        int currentIndex = 0;
                        var matches = Regex.Matches(text, @":([a-zA-Z0-9_+\-]+):");
                        if (matches.Count == 0)
                        {
                            inlines.Add(run);
                            continue;
                        }

                        foreach (Match match in matches)
                        {
                            if (match.Index > currentIndex)
                                inlines.Add(new System.Windows.Documents.Run(text.Substring(currentIndex, match.Index - currentIndex)) { FontFamily = run.FontFamily, });
                            string code = match.Value;
                            if (emojiMap.TryGetValue(code, out string url))
                            {
                                var img = new System.Windows.Controls.Image
                                {
                                    Source = new BitmapImage(new Uri(url)),
                                    Width = effectiveEmojiSize,
                                    Height = effectiveEmojiSize,
                                    Margin = margin,
                                    RenderTransform = offset
                                };
                                inlines.Add(new InlineUIContainer(img));
                            }
                            else
                            {
                                inlines.Add(new System.Windows.Documents.Run(code) { FontFamily = run.FontFamily, //Foreground = run.Foreground
                                });
                            }

                            currentIndex = match.Index + match.Length;
                        }

                        if (currentIndex < text.Length)
                            inlines.Add(new System.Windows.Documents.Run(text.Substring(currentIndex)) { FontFamily = run.FontFamily, //Foreground = run.Foreground
                            });
                        break;
                    case System.Windows.Documents.Span span:
                        var newSpan = new System.Windows.Documents.Span();
                        foreach (var i in span.Inlines)
                        {
                            var clone = CloneInline(i); // <- **Clone statt Original**
                            if (clone != null)
                                newSpan.Inlines.Add(clone);
                        }

                        ReplaceShortcodesWithImages(newSpan.Inlines, newSpan.FontSize, emojiSize, margin); // rekursiv, aber nur auf geklonte Inlines
                        inlines.Add(newSpan);
                        break;
                    default:
                        inlines.Add(inline);
                        break;
                }
            }
        }

        // Inline-Klon 
        System.Windows.Documents.Inline CloneInline(System.Windows.Documents.Inline inline)
        {
            switch (inline)
            {
                case System.Windows.Documents.Run run:
                    return new System.Windows.Documents.Run(run.Text)
                    {
                        FontFamily = run.FontFamily
                    };
                case System.Windows.Documents.Bold bold:
                    var b = new System.Windows.Documents.Bold();
                    foreach (var i in bold.Inlines)
                        b.Inlines.Add(CloneInline(i));
                    return b;
                case System.Windows.Documents.Italic italic:
                    var it = new System.Windows.Documents.Italic();
                    foreach (var i in italic.Inlines)
                        it.Inlines.Add(CloneInline(i));
                    return it;
                case System.Windows.Documents.Underline underline:
                    var u = new System.Windows.Documents.Underline();
                    foreach (var i in underline.Inlines)
                        u.Inlines.Add(CloneInline(i));
                    return u;
                case System.Windows.Documents.Span span:
                    var s = new System.Windows.Documents.Span();
                    foreach (var i in span.Inlines)
                        s.Inlines.Add(CloneInline(i));
                    return s;
                case System.Windows.Documents.InlineUIContainer ui:
                    return new System.Windows.Documents.InlineUIContainer(ui.Child);
                default:
                    return null;
            }
        }

        // Block-Kopie 
        void AddBlockCopy(System.Windows.Documents.Block block, System.Windows.Documents.BlockCollection blocks)
        {
            double? emojiSize = null;
            Thickness? emojiMargin = null;
            TranslateTransform? emojiOffset = null;
            switch (block)
            {
                case System.Windows.Documents.Paragraph p:
                    var para = new System.Windows.Documents.Paragraph();
                    foreach (var inline in p.Inlines)
                    {
                        var clone = CloneInline(inline);
                        if (clone != null)
                            para.Inlines.Add(clone);
                    }

                    string text = new TextRange(p.ContentStart, p.ContentEnd).Text.Trim();
                    if (text.StartsWith("[") && text.Contains("]"))
                    {
                        int end = text.IndexOf(']');
                        string tagName = text.Substring(1, end - 1); // z.B. "Heading1"
                        para.Tag = tagName;
                    }
                    else
                    {
                        para.Tag = p.Tag ?? "Paragraph";
                    }

                    // 3. Case anwenden
                    if (para.Tag is string tag)
                    {
                        switch (tag)
                        {
                            case "CodeBlock":
                                para.Background = Brushes.DarkSlateGray;
                                para.Foreground = Brushes.LightGreen;
                                para.FontFamily = new FontFamily("Consolas");
                                para.Margin = new Thickness(5);
                                break;
                            case "QuoteBlock":
                                para.Background = new SolidColorBrush(Color.FromArgb(40, 128, 128, 128));
                                para.Margin = new Thickness(10, 5, 5, 5);
                                para.Padding = new Thickness(10, 0, 0, 0);
                                break;
                            case "ThematicBreak":
                                para.BorderBrush = Brushes.Gray;
                                para.BorderThickness = new Thickness(0, 0, 0, 1);
                                break;
                            case "Heading1":
                                para.FontSize = 28;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(0, 0, 0, 8); // Abstand nach unten
                                break;
                            case "Heading2":
                                para.FontSize = 24;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(0, 0, 0, 0);
                                para.LineStackingStrategy = LineStackingStrategy.BlockLineHeight;
                                para.LineHeight = 24;
                                emojiSize = 26;
                                emojiMargin = new Thickness(-30, -10, 0, -10);
                                emojiOffset = new TranslateTransform(10, 5);
                                break;
                            case "Heading3":
                                para.FontSize = 16;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(10, 0, 0, 4);
                                emojiSize = 6;
                                break;
                            case "Heading4":
                                para.FontSize = 16;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(0, 0, 0, 3);
                                break;
                            case "Heading5":
                                para.FontSize = 14;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(0, 0, 0, 2);
                                break;
                            case "Heading6":
                                para.FontSize = 12;
                                para.FontWeight = FontWeights.Bold;
                                para.Margin = new Thickness(0, 0, 0, 1);
                                break;
                        }
                    }

                    // 4. Erst hier den sichtbaren Text ohne [Tag] setzen
                    if (text.StartsWith("[") && text.Contains("]"))
                    {
                        int end = text.IndexOf(']');
                        text = text.Substring(end + 1).Trim();
                        para.Inlines.Clear();
                        para.Inlines.Add(new Run(text));
                    }

                    ReplaceShortcodesWithImages(para.Inlines, para.FontSize, emojiSize, emojiMargin, emojiOffset);
                    blocks.Add(para);
                    // Nur für Heading2 den Separator hinzufügen
                    if (para.Tag?.ToString() == "Heading2")
                    {
                        var separator = new Paragraph
                        {
                            BorderBrush = Brushes.Gray,
                            BorderThickness = new Thickness(0, 0, 0, 1),
                            Margin = new Thickness(0, 0, 0, 20),
                            LineStackingStrategy = LineStackingStrategy.BlockLineHeight,
                            LineHeight = 4
                        };
                        blocks.Add(separator);
                    }

                    break;

                case System.Windows.Documents.List list:
                    var newList = new System.Windows.Documents.List
                    {
                        MarkerStyle = list.MarkerStyle,
                        Margin = new Thickness(50, 5, 0, 15),
                        Padding = new Thickness(5)
                    };
                    foreach (var li in list.ListItems)
                    {
                        var newLi = new System.Windows.Documents.ListItem();
                        foreach (var liBlock in li.Blocks)
                        {
                            AddBlockCopy(liBlock, newLi.Blocks);
                            // Prüfen, ob es eine verschachtelte Liste ist
                            if (liBlock is System.Windows.Documents.List nestedList)
                            {
                                // Prüfen, wie viele führende Whitespaces das ListItem hat
                                int leadingWsCount = CountLeadingWhitespaces(li); // <- hier musst du die Zählfunktion haben
                                //MessageBox.Show($"Count: {leadingWsCount}");
                                if (leadingWsCount == 2)
                                {
                                    nestedList.Margin = new Thickness(0, 2, 0, 2);
                                    nestedList.LineHeight = 14;
                                    nestedList.LineStackingStrategy = LineStackingStrategy.BlockLineHeight;
                                }
                            }
                        }

                        newLi.Margin = new Thickness(0, 2, 0, 2);
                        newList.ListItems.Add(newLi);
                    }

                    blocks.Add(newList);
                    break;
                /*   marker geht emoji nicht margin bringt nichts              case System.Windows.Documents.List list:
                {
                    //MessageBox.Show("Start processing List");
                    var newList = new System.Windows.Documents.List
                    {
                        MarkerStyle = list.MarkerStyle,
                        Margin = new Thickness(50, 5, 0, 15),
                        Padding = new Thickness(5)
                    };

                    foreach (var li in list.ListItems)
                    {
                        var newLi = new ListItem();
                        try
                        {
                            // --- 1. Kopie aller Blocks ---
                            var originalBlocks = li.Blocks.OfType<Block>().ToList();

                            int leadingWsCount = 0;
                            string newTextAfterMarker = null;

                            // --- 2. Marker auslesen (nur erste Paragraph) ---
                            if (originalBlocks.FirstOrDefault() is Paragraph firstpara)
                            {
                                var allText = string.Concat(firstpara.Inlines.OfType<Run>().Select(r => r.Text));
                                //MessageBox.Show($"ListItem raw text: '{allText}'");

                                var match = Regex.Match(allText, @"^\s*-?\s*\[(\d+)\]");
                                if (match.Success && int.TryParse(match.Groups[1].Value, out int count))
                                {
                                    leadingWsCount = count;
                                    newTextAfterMarker = allText.Substring(match.Length).TrimStart();
                                    //MessageBox.Show($"Marker gefunden: {leadingWsCount}");
                                }
                                else
                                {
                                    MessageBox.Show("Kein Marker gefunden, Tag = 0");
                                }
                            }

                            li.Tag = leadingWsCount;

                            // --- 3. Alle Blocks kopieren ---
                            foreach (var blockCopy in originalBlocks)
                            {
                                try
                                {
                                    //MessageBox.Show($"AddBlockCopy für BlockType: {blockCopy.GetType()}");
                                    AddBlockCopy(blockCopy, newLi.Blocks);

                                    // Margin nur bei nestedList & leadingWs == 2
                                    if (li.Tag is int leadingWs && leadingWs == 2)
                                    {
                                        newLi.Margin = new Thickness(150, 150, 150, 10);
                                        newLi.LineHeight = 14;
                                        //newLi.LineStackingStrategy = LineStackingStrategy.BlockLineHeight;
                                        //MessageBox.Show("NestedList Margin für leadingWs=2 gesetzt");
                                    }
                                }
                                catch (Exception exBlock)
                                {
                                    MessageBox.Show($"Error in liBlock: {exBlock}");
                                }
                            }

                            // --- 4. Marker erst jetzt entfernen ---
                            if (newTextAfterMarker != null && newLi.Blocks.FirstBlock is Paragraph paraToUpdate)
                            {
                                paraToUpdate.Inlines.Clear();
                                paraToUpdate.Inlines.Add(new Run(newTextAfterMarker));
                                //MessageBox.Show($"Text nach Entfernen des Markers: '{newTextAfterMarker}'");
                            }

                            newLi.Margin = new Thickness(0, 2, 0, 2);
                            newList.ListItems.Add(newLi);
                            //MessageBox.Show("ListItem hinzugefügt");
                        }
                        catch (Exception exLi)
                        {
                            MessageBox.Show($"Error in ListItem: {exLi}");
                        }
                    }

                    try
                    {
                        blocks.Add(newList);
                        //MessageBox.Show("List erfolgreich hinzugefügt");
                    }
                    catch (Exception exList)
                    {
                        MessageBox.Show($"Error adding newList: {exList}");
                    }
                    break;
                } */
                case System.Windows.Documents.Table table:
                    var newTable = new System.Windows.Documents.Table
                    {
                        CellSpacing = table.CellSpacing,
                        Background = table.Background
                    };
                    foreach (var rowGroup in table.RowGroups)
                    {
                        var newRowGroup = new System.Windows.Documents.TableRowGroup();
                        foreach (var row in rowGroup.Rows)
                        {
                            var newRow = new System.Windows.Documents.TableRow();
                            foreach (var cell in row.Cells)
                            {
                                var newCell = new System.Windows.Documents.TableCell();
                                foreach (var cBlock in cell.Blocks)
                                    AddBlockCopy(cBlock, newCell.Blocks);
                                newRow.Cells.Add(newCell);
                            }

                            newRowGroup.Rows.Add(newRow);
                        }

                        newTable.RowGroups.Add(newRowGroup);
                    }

                    blocks.Add(newTable);
                    break;
                case System.Windows.Documents.Section section:
                    foreach (var secBlock in section.Blocks)
                        AddBlockCopy(secBlock, blocks);
                    break;
                default:
                    break;
            }
        }

        int CountLeadingWhitespaces(System.Windows.Documents.ListItem li)
        {
            // Erstes Block prüfen
            if (li.Blocks.FirstBlock is System.Windows.Documents.Paragraph para)
            {
                string text = new TextRange(para.ContentStart, para.ContentEnd).Text;
                int count = 0;
                foreach (char c in text)
                {
                    if (c == ' ')
                        count++;
                    else
                        break;
                }

                return count;
            }

            return 0;
        }

        // Hauptlogik 
        foreach (var block in sourceDoc.Blocks)
            AddBlockCopy(block, targetDoc.Blocks);
        richTextBox.Document = targetDoc;
    }
    ///
    /// ||===================================== End =====================================||
    ///


    ///
    /// ||=============================================================================================================||
    /// || ====== DE: Schließfunktion für alle UI-Elemente und Dispatcher - entladed das Script korrekt ============== ||
    /// || ======  EN: Close function for all UI elements and Dispatcher - unloads the script correctly ============== ||
    /// ||=============================================================================================================||
    /// 
    private void DisposeUI()
    {
        try
        {
            if (currentWindow != null)
            {
                if (currentWindow.Dispatcher != null && !currentWindow.Dispatcher.HasShutdownStarted)
                {
                    if (currentWindow.Dispatcher.CheckAccess())
                    {
                        if (currentWindow.IsVisible)
                            currentWindow.Close();
                    }
                    else
                    {
                        try
                        {
                            currentWindow.Dispatcher.Invoke(() =>
                            {
                                if (currentWindow.IsVisible)
                                    currentWindow.Close();
                            });
                        }
                        catch
                        {

                        }
                    }
                }
            }


            if (uiDispatcher != null && !uiDispatcher.HasShutdownStarted)
            {
                try
                {
                    uiDispatcher.InvokeShutdown();
                }
                catch
                {

                }
            }
        }
        catch
        {

        }
        finally
        {


            WriteLog("DisposeUI - disposed correct" , "Debug");
            currentWindow = null;
            uiDispatcher = null;
            uiThread = null;
            _ViewModel = null;
        }
    }

    public void WriteLog(string logMessage, string level = "Debug")
    {
        string message = $"STEVO_Category_Changer :: {logMessage}";

        switch (level.ToLower())
        {
            case "info":
                CPH.LogInfo(message);
                break;
            case "warn":
            case "warning":
                CPH.LogWarn(message);
                break;
            case "error":
                CPH.LogError(message);
                break;
            case "verbose":
                CPH.LogVerbose(message);
                break;
            default:
                CPH.LogDebug(message);
                break;
        }
    }
 
    public void Dispose()
    {
        DisposeUI();
    }
}