using LicencePlateApi.Helpers;
using LicencePlateApi.Models;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace LicencePlateApi.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class PlateController : ControllerBase
    {
        private List<PlateInformation> plates = new List<PlateInformation>();

        public PlateController()
        {
            if (System.IO.File.Exists(AppConstants.DataFilePath))
            {
                try
                {
                    var content = System.IO.File.ReadAllText(AppConstants.DataFilePath);
                    plates = JsonSerializer.Deserialize<List<PlateInformation>>(content) ?? new List<PlateInformation>();
                }
                catch
                {
                    Console.WriteLine("Unable to read data file.");
                }
            }
        }

        [HttpGet("infos")]
        public IEnumerable<PlateInformation> GetInfos()
        {
            return plates;
        }

        [HttpGet("info")]
        public ActionResult<PlateInformation> GetInfo(string plateId)
        {
            var plate = plates.FirstOrDefault(f => f.Plate.ToLower() == plateId.ToLower());
            if (plate == null)
            {
                return NotFound("Not found");
            }
            return plate;
        }
    }
}
