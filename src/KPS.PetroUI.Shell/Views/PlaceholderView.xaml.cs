using System.Windows;
using System.Windows.Controls;

namespace KPS.PetroUI.Shell.Views;

public partial class PlaceholderView : UserControl
{
    public static readonly DependencyProperty MessageProperty =
        DependencyProperty.Register(nameof(Message), typeof(string), typeof(PlaceholderView), new PropertyMetadata(string.Empty));

    public string Message
    {
        get => (string)GetValue(MessageProperty);
        set => SetValue(MessageProperty, value);
    }

    public PlaceholderView()
    {
        InitializeComponent();
    }
}
