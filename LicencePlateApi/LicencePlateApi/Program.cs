using LicencePlateApi.Helpers;

namespace LicencePlateApi
{
    public class Program
    {
        public static void Main(string[] args)
        {
            // Create data folder.
            if (!Directory.Exists(AppConstants.DataFolder))
            {
                Directory.CreateDirectory(AppConstants.DataFolder);
                if (!File.Exists(AppConstants.DataFilePath))
                {
                    File.WriteAllText(AppConstants.DataFilePath, "[]");
                }
            }

            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.

            builder.Services.AddControllers();

            var app = builder.Build();

            // Configure the HTTP request pipeline.

            app.UseAuthorization();


            app.MapControllers();

            app.Run();
        }
    }
}
