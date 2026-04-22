using System.Windows.Controls;
using System.Windows.Threading;
using KPS.PetroUI.Shell.ViewModels;

namespace KPS.PetroUI.Shell.Controls;

public partial class StatusBarControl : UserControl
{
    private DispatcherTimer? _clock;

    public StatusBarControl()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => EnsureClock();
    }

    private void EnsureClock()
    {
        if (_clock is not null || DataContext is not MainWindowViewModel vm) return;
        _clock = new DispatcherTimer(DispatcherPriority.Background) { Interval = TimeSpan.FromSeconds(1) };
        _clock.Tick += (_, _) => vm.Clock = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        _clock.Start();
    }
}
