

protocol =  {
  "refs": {
    "{{pcr_reaction_plate}}": {
      "id": "{{pcr_reaction_plate_id}}",
      "store": {
        "where": "cold_20"
      }
    },
    "{{primers}}": {
      "id": "{{primers_id}}",
      "store": {
        "where": "cold_20"
      }
    },
    "{{sample}}": {
      "id": "{{sample_id}}",
      "store": {
        "where": "cold_20"
      }
    },
    "{{pcr_mix}}": {
      "id": "{{pcr_mix_id}}",
      "store": {
        "where": "cold_20"
      }
    },
    "{{water}}": {
      "id": "{{water_id}}",
      "store": {
        "where": "ambient"
      }
    },
    "{{amplified_libraries}}": {
      "id": "{{amplified_libraries_id}}",
      "store": {
        "where": "cold_20"
      }
    },
  },
  "instructions": [
    {
      "groups": [
        {
          "transfer": [
            {
              "volume": "22.5:microliter",
              "to": "{{pcr_reaction_plate}}/{{reaction_well}}",
              "from": "{{pcr_mix}}/0"
            }
          ]
        },
        {
          "transfer": [
            {
              "volume": "5.0:microliter",
              "to": "{{pcr_reaction_plate}}/{{reaction_well}}",
              "from": "{{sample}}/0"
            }
          ]
        },
        {
          "transfer": [
            {
              "volume": "1.25:microliter",
              "to": "{{pcr_reaction_plate}}/{{reaction_well}}",
              "from": "{{primers}}/0"
            }
          ]
        }
      ],
      "op": "pipette"
    },
    {
      "object": "{{pcr_reaction_plate}}",
      "op": "seal"
    },
    {
      "volume": "30:microliter",
      "dataref": null,
      "object": "{{pcr_reaction_plate}}",
      "groups": [
        {
          "cycles": 1,
          "steps": [
            {
              "duration": "120:second",
              "temperature": "94:celsius"
            }
          ]
        },
        {
          "cycles": 30,
          "steps": [
            {
              "duration": "45:second",
              "temperature": "94:celsius"
            },
            {
              "duration": "60:second",
              "temperature": "55:celsius"
            },
            {
              "duration": "90:second",
              "temperature": "72:celsius"
            }
          ]
        },
        {
          "cycles": 1,
          "steps": [
            {
              "duration": "600:second",
              "temperature": "72:celsius"
            },
            {
              "duration": "600:second",
              "temperature": "8:celsius"
            }
          ]
        }
      ],
      "op": "thermocycle"
    },
    {
      "object": "{{pcr_reaction_plate}}",
      "op": "unseal"
    },
    {
      "object": "{{amplified_libraries}}",
      "op": "unseal"
    },
    {
      "groups": [
        {
          "transfer": [
            {
              "volume": "25:microliter",
              "to": "{{pcr_reaction_plate}}/{{output_well}}",
              "from": "{{pcr_reaction_plate}}/{{reaction_well}}"
            }
          ]
        }
      ],
      "op": "pipette"
    },
    {
      "object": "{{pcr_reaction_plate}}",
      "op": "seal"
    },
    {
      "object": "{{amplified_libraries}}",
      "op": "seal"
    }
  ]
}

