using CommunityToolkit.Mvvm.Messaging.Messages;
using KPS.PetroUI.Core.Models;

namespace KPS.PetroUI.Core.Events;

public sealed class UserLoggedInMessage(User user) : ValueChangedMessage<User>(user);

public sealed class UserLoggedOutMessage() : ValueChangedMessage<bool>(true);

public sealed class NavigationRequestedMessage(string documentKey, string title, object? parameter = null)
{
    public string DocumentKey { get; } = documentKey;
    public string Title { get; } = title;
    public object? Parameter { get; } = parameter;
}

public sealed class JobUpdatedMessage(int jobId) : ValueChangedMessage<int>(jobId);

public sealed class JobCompletedMessage(int jobId) : ValueChangedMessage<int>(jobId);
