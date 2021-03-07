#!/usr/bin/env python3

import emails
import json
import locale
import operator
import os
import reports
import sys


def load_data(filename):
    """Loads the contents of filename as a JSON file."""
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def format_car(car):
    """Given a car dictionary, returns a nicely formatted name."""
    return "{} {} ({})".format(
        car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
    """Analyzes the data, looking for maximums.

    Returns a list of lines that summarize the information.
    """
    max_revenue = {"revenue": 0}
    max_sales = {"total_sales": 0}
    popular_year = {}

    for item in data:
        # Calculate the revenue generated by this model (price * total_sales)
        # We need to convert the price from "$1234.56" to 1234.56
        item_price = locale.atof(item["price"].strip("$"))
        item_revenue = item["total_sales"] * item_price
        if item_revenue > max_revenue["revenue"]:
            item["revenue"] = item_revenue
            max_revenue = item

        # Set car model with max sales
        total_sales = item["total_sales"]
        if total_sales > max_sales["total_sales"]:
            max_sales = item

        # Set the most popular year
        car_year = item["car"]["car_year"]
        if car_year not in popular_year:
            popular_year[car_year] = total_sales
        else:
            popular_year[car_year] += total_sales

    most_popular_year = sorted(popular_year.items(), key=operator.itemgetter(1), reverse=True)

    summary = [
        "The {} generated the most revenue: ${}".format(
            format_car(max_revenue["car"]), max_revenue["revenue"]),
        "The {} had the most sales: {}".format(
            format_car(max_sales["car"]), max_sales["total_sales"]),
        "The most popular year was {} with {} sales.".format(
            most_popular_year[0][0], most_popular_year[0][1])
    ]

    return summary


def cars_dict_to_table(car_data):
    """Turns the data in car_data into a list of lists."""
    table_data = [["ID", "Car", "Price", "Total Sales"]]
    for item in car_data:
        table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
    return table_data


def main(argv):
    """Process the JSON data and generate a full report out of it."""
    data = load_data("car_sales.json")
    summary = process_data(data)
    file_name = "cars.pdf"

    # For Windows
    destination_dir = os.path.join(os.path.abspath("/"), os.getcwd(), "tmp")

    # For Linux
    # destination_dir = os.path.join(os.path.abspath("/"), "tmp", file_name)

    # Make destination directory
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    destination_file = os.path.join(destination_dir, file_name)

    # Generate PDF
    title = "Sales summary for last month"
    additional_info = "<br/>".join(summary)
    table_data = cars_dict_to_table(data)

    reports.generate(destination_file, title, additional_info, table_data)

    # Generate Email
    # TODO: Change recipient
    sender = "automation@example.com"
    recipient = "student-02-e83eddc447a8@example.com"
    subject = "Sales summary for last month"
    body = "\n".join(summary)

    # Generate email
    message = emails.generate(sender, recipient, subject, body, destination_file)
    # Send email
    emails.send(message)


if __name__ == "__main__":
    main(sys.argv)
