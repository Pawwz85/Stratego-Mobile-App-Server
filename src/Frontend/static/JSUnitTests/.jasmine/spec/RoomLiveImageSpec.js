// LiveChatImage.spec.js
describe('LiveChatImage', () => {
    let serverConnectionMock;
    let liveChatImage;

    beforeEach(() => {
        serverConnectionMock = {
            send_request: jasmine.createSpy('send_request').and.returnValue(Promise.resolve({ status: "success" })),
        };
        liveChatImage = new LiveChatImage(serverConnectionMock, 123);
    });

    it('should add a message in the correct order', () => {
        const msg1 = { orderNumber: 1, username: 'user1', content: 'Hello' };
        const msg2 = { orderNumber: 3, username: 'user2', content: 'Hi' };
        const msg3 = { orderNumber: 2, username: 'user3', content: 'Hey' };

        liveChatImage.add_message(msg1);
        liveChatImage.add_message(msg2);
        liveChatImage.add_message(msg3);

        expect(liveChatImage.orderedMessagesList).toEqual([msg1, msg3, msg2]);
    });

    it('should throw an error if orderNumber is not a number', () => {
        const msg = { orderNumber: 'not-a-number', username: 'user', content: 'Hello' };

        expect(() => liveChatImage.add_message(msg)).toThrowError(TypeError);
    });

    it('should correctly transform a protocol message to a component message', () => {
        const msg = { nr: 1, nickname: 'user', message: 'Hello' };
        const transformedMsg = liveChatImage.__protocol_message_to_component_message(msg);

        expect(transformedMsg).toEqual({ orderNumber: 1, username: 'user', content: 'Hello' });
    });

    it('should call serverConnection.send_request with correct parameters when syncing', async () => {
        await liveChatImage.sync();

        expect(serverConnectionMock.send_request).toHaveBeenCalledWith(
            { type: "get_chat_metadata", room: 123 },
            10000
        );

        expect(serverConnectionMock.send_request).toHaveBeenCalledWith(
            jasmine.objectContaining({ type: "get_chat_messages", room: 123 }),
            10000
        );
    });

    it('should add a message when handle_chat_event receives a valid event', () => {
        const event = { nr: 1, nickname: 'user', message: 'Hello', room_id: 123 };

        liveChatImage.handle_chat_event(event);

        expect(liveChatImage.orderedMessagesList.length).toBe(1);
        expect(liveChatImage.orderedMessagesList[0]).toEqual({
            orderNumber: 1,
            username: 'user',
            content: 'Hello',
        });
    });

    it('should ignore event if room_id does not match', () => {
        const event = { nr: 1, nickname: 'user', message: 'Hello', room_id: 999 };

        liveChatImage.handle_chat_event(event);

        expect(liveChatImage.orderedMessagesList.length).toBe(0);
    });
});
// BoardLiveImage.spec.js
describe('BoardLiveImage', () => {
    let serverConnectionMock;
    let boardLiveImage;
    const empty_board_mock = new Array(100).fill(null);

    beforeEach(() => {
        serverConnectionMock = {
            
            send_request: jasmine.createSpy('send_request').and.returnValue(Promise.resolve({ status: "success", game_status: 'playing', board: empty_board_mock})),
        };
        boardLiveImage = new BoardLiveImage(serverConnectionMock, 123);
    });

    it('should update the order number, phase, and position on handle_board_event', () => {
        const event = { nr: 2, game_status: 'playing', board: empty_board_mock };

        boardLiveImage.handle_board_event(event);

        expect(boardLiveImage.orderNumber).toBe(2);
        expect(boardLiveImage.phase).toBe('playing');
        expect(boardLiveImage.position).toEqual(empty_board_mock);
    });

    it('should call serverConnection.send_request with correct parameters when syncing', async () => {
        await boardLiveImage.sync();

        expect(serverConnectionMock.send_request).toHaveBeenCalledWith(
            { type: "get_board", room_id: 123 }
        );
    });

    it('should add an observer and notify it instantly', () => {
        const observerMock = jasmine.createSpyObj('observer', ['update']);

        boardLiveImage.add_observer(observerMock);

        expect(observerMock.update).toHaveBeenCalledWith(boardLiveImage);
        expect(boardLiveImage.observers).toContain(observerMock);
    });
});

// GamePhaseLiveImage.spec.js
describe('GamePhaseLiveImage', () => {
    let boardLiveImage;
    let gamePhaseLiveImage;

    beforeEach(() => {
        boardLiveImage = new BoardLiveImage({}, 123);
        gamePhaseLiveImage = new GamePhaseLiveImage(boardLiveImage);
    });

    it('should notify observers when game phase changes', () => {
        const observerMock = jasmine.createSpyObj('observer', ['update_phase']);

        gamePhaseLiveImage.add_observer(observerMock);

        boardLiveImage.phase = 'playing';
        gamePhaseLiveImage.update(boardLiveImage);

        expect(observerMock.update_phase).toHaveBeenCalledWith('playing');
    });

    it('should notify observer immediately when added', () => {
        const observerMock = jasmine.createSpyObj('observer', ['update_phase']);

        gamePhaseLiveImage.add_observer(observerMock);

        expect(observerMock.update_phase).toHaveBeenCalled();
    });
});

describe('BoardPositionLiveImage', function(){
    let boardLiveImage;
    let positionliveImage;

    beforeEach(() => {
        boardLiveImage = new BoardLiveImage({}, 123);
        positionliveImage = new BoardPositionLiveImage(boardLiveImage);
    })

    //TODO: write some test cases
})