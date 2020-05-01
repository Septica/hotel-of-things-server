window.onload = getAllRooms;

const detailEl = document.getElementById('room-details');
const roomList = document.getElementById('room-list');
const blackBackground = document.getElementsByClassName('black-background')[0]

async function getAllRooms() {
    const response = await fetch('/rooms');

    updateRoomList(await response.json());
}

async function createNewRoom(event) {
    event.preventDefault();

    const formEl = event.target;
    const formData = new FormData(formEl);
    const response = await fetch('/rooms', {
        method: 'PUT',
        body: new URLSearchParams(formData)
    });

    updateRoomList(await response.json());
    formEl.reset()
}

async function deleteRoom(roomNumber) {
    const response = await fetch(`/rooms/${roomNumber}`, {
        method: 'DELETE'
    });

    updateRoomList(await response.json());
    detailEl.innerHTML = '';
}

function updateRoomList(rooms) {
    roomList.innerHTML = rooms.reduce((accumulator, room_number) => accumulator += `<tr><th scope="row">${room_number}</th><td><i class="mdi mdi-pencil edit-button" onclick="getRoomDetails('${room_number}')"></i></td></tr>`, '');
}

async function getRoomDetails(roomNumber) {
    const response = await fetch(`/rooms/${roomNumber}`);

    updateRoomDetails(await response.json());
}

async function connectDeviceToARoom(roomNumber, event) {
    event.preventDefault();

    const formEl = event.target;
    const formData = new FormData(formEl);
    const response = await fetch(`/rooms/${roomNumber}/devices`, {
        method: 'PUT',
        body: new URLSearchParams(formData)
    });

    updateRoomDetails(await response.json());
    formEl.reset()
}

async function disconnectAllDevicesFromARoom(roomNumber) {
    const response = await fetch(`/rooms/${roomNumber}/devices`, {
        method: 'DELETE'
    });

    updateRoomDetails(await response.json());
}

async function disconnectDeviceFromARoom(room_number, macAddress) {
    const response = await fetch(`/rooms/${room_number}/devices/${macAddress}`, {
        method: 'DELETE'
    });

    updateRoomDetails(await response.json());
}

function closeEdit() {
    console.log("helloo")
    blackBackground.classList.remove('black-background--show')
    detailEl.innerHTML=``
}

function updateRoomDetails({ room_number, devices }) {
    blackBackground.classList.add('black-background--show')
    detailEl.innerHTML = `
        <div class="close-button"><i class="mdi mdi-close" onclick="closeEdit()"></i></div>
        <h1>${room_number}</h1>
        <button onclick="deleteRoom('${room_number}')")>Delete Room</button>
        <button onclick="disconnectAllDevicesFromARoom('${room_number}')">Disconnect All</button>
        <ul>
            ${devices.reduce((accumulator, [macAddress, state]) => accumulator += `
                <li>
                    <span>${macAddress}</span>
                    <span>${state}</span>
                    <button onclick="disconnectDeviceFromARoom('${room_number}', '${macAddress}')">Disconnect</button>
                </li>
            `, '')}
        </ul>
        <form onsubmit="connectDeviceToARoom('${room_number}', event)">
            <input name="mac_address" />
            <button>Connect New Device</button>
        </form>
    `;
}